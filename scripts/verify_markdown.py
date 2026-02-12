#!/usr/bin/env python3
"""
Verify Jekyll markdown content before publication.

Checks:
- Required traceability front matter: verified_at + (source_url or sources)
- Citation allowlist: all outbound http(s) URLs must be on allowlist (host-based)
- Link reachability: outbound URLs must return <400 (unless excepted)
- News re-verification: if source_type == "news", its source URL(s) must be reachable

Outputs:
- verification/manifest.json (machine-readable traceability + results)
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

import httpx
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST_PATH = REPO_ROOT / "verification" / "allowlist.yml"
EXCEPTIONS_PATH = REPO_ROOT / "verification" / "exceptions.yml"
MANIFEST_PATH = REPO_ROOT / "verification" / "manifest.json"

IN_SCOPE_DIRS = [
    REPO_ROOT / "_pages",
    REPO_ROOT / "_posts",
]

EXCLUDE_DIR_NAMES = {
    ".git",
    ".github",
    "_site",
    "node_modules",
    "vendor",
}

URL_RE = re.compile(r"https?://[^\s<>()\[\]\"']+")
EXAMPLE_URL_SUBSTRINGS = (
    "yourusername.github.io/",
    "sweeden-ttu.github.io/myblog",
    "sweeden-ttu.github.io",
    "github.io/project",
)


class VerificationError(Exception):
    pass


@dataclass(frozen=True)
class AllowHostRule:
    host: str
    allow_subdomains: bool
    category: str = "unspecified"


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        raise VerificationError(f"Missing required config file: {path}")
    data = yaml.safe_load(_read_text(path)) or {}
    if not isinstance(data, dict):
        raise VerificationError(f"Config file must be a mapping: {path}")
    return data


def _iter_markdown_files() -> List[Path]:
    files: List[Path] = []
    for base in IN_SCOPE_DIRS:
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            if any(part in EXCLUDE_DIR_NAMES for part in p.parts):
                continue
            files.append(p)
    return sorted(files)


def _split_front_matter(text: str) -> Tuple[Optional[str], str]:
    """
    Returns (front_matter_yaml, body). If no front matter, returns (None, full_text).
    """
    if not text.startswith("---\n"):
        return None, text
    # Find the second delimiter
    idx = text.find("\n---\n", 4)
    if idx == -1:
        return None, text
    fm = text[4:idx]
    body = text[idx + len("\n---\n") :]
    return fm, body


def _parse_front_matter(path: Path, text: str) -> Dict[str, Any]:
    fm, _ = _split_front_matter(text)
    if fm is None:
        raise VerificationError(f"{path}: missing YAML front matter")
    data = yaml.safe_load(fm) or {}
    if not isinstance(data, dict):
        raise VerificationError(f"{path}: front matter must be a mapping")
    return data


def _extract_urls_from_text(text: str) -> List[str]:
    urls = URL_RE.findall(text)
    cleaned: List[str] = []
    for u in urls:
        # Strip common trailing punctuation
        u2 = u.rstrip("`'\".,);:!?]")
        cleaned.append(u2)
    return cleaned


def _normalize_host(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None
    # Remove credentials/port
    host = parsed.hostname
    if not host:
        return None
    host = host.lower()
    # Ignore local/dev-only links in content (tutorial posts, local setup)
    if host in {"localhost", "127.0.0.1"}:
        return None
    return host


def _load_allowlist() -> List[AllowHostRule]:
    raw = _load_yaml(ALLOWLIST_PATH)
    hosts = raw.get("hosts", [])
    if not isinstance(hosts, list):
        raise VerificationError(f"{ALLOWLIST_PATH}: 'hosts' must be a list")
    rules: List[AllowHostRule] = []
    for item in hosts:
        if not isinstance(item, dict):
            raise VerificationError(f"{ALLOWLIST_PATH}: each host entry must be a mapping")
        host = item.get("host")
        allow_subdomains = item.get("allow_subdomains", False)
        category = item.get("category", "unspecified")
        if not isinstance(host, str) or not host.strip():
            raise VerificationError(f"{ALLOWLIST_PATH}: host entry missing 'host'")
        if not isinstance(allow_subdomains, bool):
            raise VerificationError(f"{ALLOWLIST_PATH}: allow_subdomains must be boolean for host={host}")
        if not isinstance(category, str):
            category = "unspecified"
        rules.append(AllowHostRule(host=host.lower(), allow_subdomains=allow_subdomains, category=category))
    return rules


def _host_is_allowed(host: str, rules: List[AllowHostRule]) -> bool:
    host = host.lower().strip(".")
    for rule in rules:
        if host == rule.host:
            return True
        if rule.allow_subdomains and host.endswith("." + rule.host):
            return True
    return False


def _collect_traceability_urls(front_matter: Dict[str, Any]) -> List[str]:
    urls: List[str] = []
    source_url = front_matter.get("source_url")
    if isinstance(source_url, str) and source_url.strip():
        urls.append(source_url.strip())
    sources = front_matter.get("sources")
    if isinstance(sources, list):
        for s in sources:
            if isinstance(s, dict):
                u = s.get("url")
                if isinstance(u, str) and u.strip():
                    urls.append(u.strip())
    return urls


def _require_traceability(path: Path, front_matter: Dict[str, Any], exempt_files: set[str]) -> None:
    rel = str(path.relative_to(REPO_ROOT))
    if rel in exempt_files:
        return

    verified_at = front_matter.get("verified_at")
    if not isinstance(verified_at, (str, dt.date)):
        raise VerificationError(f"{rel}: missing required front matter field 'verified_at'")

    trace_urls = _collect_traceability_urls(front_matter)
    if not trace_urls:
        raise VerificationError(f"{rel}: must include 'source_url' or 'sources' in front matter")

    # Validate URLs parse as http(s)
    bad: List[str] = []
    for u in trace_urls:
        host = _normalize_host(u)
        if host is None:
            bad.append(u)
    if bad:
        raise VerificationError(f"{rel}: invalid traceability URL(s): {bad}")


def _load_exceptions() -> dict:
    raw = _load_yaml(EXCEPTIONS_PATH)
    for key in [
        "skip_reachability_urls",
        "skip_reachability_hosts",
        "extra_allowlist_hosts",
        "exempt_traceability_files",
    ]:
        val = raw.get(key, [])
        if val is None:
            raw[key] = []
        elif not isinstance(val, list):
            raise VerificationError(f"{EXCEPTIONS_PATH}: '{key}' must be a list")
    return raw


def _http_check_urls(
    urls: Iterable[str],
    *,
    skip_urls: set[str],
    skip_hosts: set[str],
) -> Dict[str, Dict[str, Any]]:
    """
    Returns per-url result object. Raises no exceptions; failures recorded.
    """
    results: Dict[str, Dict[str, Any]] = {}
    unique = sorted(set(urls))
    timeout = httpx.Timeout(connect=10.0, read=20.0, write=10.0, pool=10.0)
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
    headers = {"User-Agent": "legal-luminary-verifier/0.1 (+https://www.legalluminary.com)"}

    with httpx.Client(follow_redirects=True, timeout=timeout, limits=limits, headers=headers) as client:
        for url in unique:
            host = _normalize_host(url)
            host_is_skipped = False
            if host:
                host_is_skipped = host in skip_hosts or any(host.endswith("." + h) for h in skip_hosts)
            if url in skip_urls or host_is_skipped:
                results[url] = {"skipped": True, "ok": True, "status": None, "final_url": None, "error": None}
                continue

            ok = False
            status: Optional[int] = None
            final_url: Optional[str] = None
            err: Optional[str] = None

            try:
                r = client.head(url)
                status = r.status_code
                final_url = str(r.url)
                if status == 405:
                    r = client.get(url)
                    status = r.status_code
                    final_url = str(r.url)
                ok = status < 400
            except Exception as e:
                err = f"{type(e).__name__}: {e}"

            results[url] = {
                "skipped": False,
                "ok": bool(ok),
                "status": status,
                "final_url": final_url,
                "error": err,
            }
    return results


def _is_example_url(url: str) -> bool:
    u = url.lower()
    return any(s in u for s in EXAMPLE_URL_SUBSTRINGS)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["ci"], default="ci")
    args = parser.parse_args(argv)

    allow_rules = _load_allowlist()
    exceptions = _load_exceptions()

    skip_reachability_urls = {str(u) for u in exceptions["skip_reachability_urls"]}
    skip_reachability_hosts = {str(h).lower() for h in exceptions["skip_reachability_hosts"]}
    extra_allow_hosts = {str(h).lower() for h in exceptions["extra_allowlist_hosts"]}
    exempt_traceability_files = {str(p) for p in exceptions["exempt_traceability_files"]}

    allow_rules = allow_rules + [AllowHostRule(host=h, allow_subdomains=True, category="exception") for h in extra_allow_hosts]

    md_files = _iter_markdown_files()
    if not md_files:
        raise VerificationError("No markdown files found in-scope (_pages/, _posts/).")

    now = dt.datetime.now(dt.timezone.utc).isoformat()
    manifest: Dict[str, Any] = {
        "generated_at": now,
        "repo": os.environ.get("GITHUB_REPOSITORY"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "sha": os.environ.get("GITHUB_SHA"),
        "in_scope_dirs": [str(p.relative_to(REPO_ROOT)) for p in IN_SCOPE_DIRS],
        "files": {},
        "summary": {"files_total": len(md_files), "files_ok": 0, "files_failed": 0},
    }

    all_urls_for_reachability: List[str] = []
    errors: List[str] = []

    for path in md_files:
        rel = str(path.relative_to(REPO_ROOT))
        raw = _read_text(path)
        front = {}
        file_errs: List[str] = []

        try:
            front = _parse_front_matter(path, raw)
            _require_traceability(path, front, exempt_traceability_files)
        except Exception as e:
            file_errs.append(str(e))

        fm_yaml, body = _split_front_matter(raw)
        body_urls = _extract_urls_from_text(body)
        trace_urls = _collect_traceability_urls(front) if front else []
        all_urls = sorted(set(trace_urls + body_urls))

        # Allowlist check
        not_allowed: List[str] = []
        for u in all_urls:
            host = _normalize_host(u)
            if host is None:
                continue
            if not _host_is_allowed(host, allow_rules):
                not_allowed.append(u)
        if not_allowed:
            file_errs.append(f"{rel}: non-allowlisted URL(s): {not_allowed}")

        # Reachability targets (only http(s), allowlisted OR not? We enforce for all http(s) links)
        for u in all_urls:
            host = _normalize_host(u)
            if host is None:
                continue
            if _is_example_url(u):
                continue
            all_urls_for_reachability.append(u)

        file_ok = len(file_errs) == 0
        if not file_ok:
            errors.extend(file_errs)

        manifest["files"][rel] = {
            "sha256": _sha256_bytes(raw.encode("utf-8")),
            "front_matter": {
                "has_source_url": bool(isinstance(front.get("source_url"), str) and front.get("source_url", "").strip()) if front else False,
                "has_sources": bool(isinstance(front.get("sources"), list) and len(front.get("sources") or []) > 0) if front else False,
                "verified_at": (
                    front.get("verified_at").isoformat()
                    if isinstance(front.get("verified_at"), dt.date)
                    else front.get("verified_at")
                )
                if front
                else None,
                "source_type": front.get("source_type") if front else None,
            },
            "urls": all_urls,
            "errors": file_errs,
        }

    # Reachability check (global cache)
    reachability_results = _http_check_urls(
        all_urls_for_reachability,
        skip_urls=skip_reachability_urls,
        skip_hosts=skip_reachability_hosts,
    )
    manifest["reachability"] = reachability_results

    # Attach per-file reachability failures
    for rel, info in manifest["files"].items():
        file_urls: List[str] = info.get("urls", [])
        bad = []
        for u in file_urls:
            host = _normalize_host(u)
            if host is None:
                continue
            r = reachability_results.get(u)
            if r and not r.get("ok", False):
                bad.append({"url": u, **r})
        if bad:
            info["errors"].append(f"{rel}: unreachable URL(s): {bad}")

        ok = len(info["errors"]) == 0
        info["ok"] = ok

    files_ok = sum(1 for _rel, info in manifest["files"].items() if info.get("ok"))
    files_failed = len(manifest["files"]) - files_ok
    manifest["summary"]["files_ok"] = files_ok
    manifest["summary"]["files_failed"] = files_failed

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    if files_failed > 0:
        # Print a concise failure list for CI logs.
        print("Verification failed:")
        for rel, info in manifest["files"].items():
            if info.get("ok"):
                continue
            for e in info.get("errors", []):
                print(f"- {e}")
        print(f"\nWrote manifest: {MANIFEST_PATH}")
        return 2

    print(f"Verification passed ({files_ok} files). Wrote manifest: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as e:
        print(f"Verification configuration error: {e}", file=sys.stderr)
        raise SystemExit(2)

