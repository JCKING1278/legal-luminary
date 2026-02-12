"""Node 1: Extract content from markdown files.

Discovers markdown files, parses YAML front matter, validates traceability,
extracts URLs, and computes file hashes.
"""

from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ..config import EXCLUDE_DIR_NAMES, IN_SCOPE_DIRS, REPO_ROOT, VerificationError
from ..state import VerificationState
from ..url_utils import extract_urls_from_text, normalize_host


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
    """Returns (front_matter_yaml, body). If no front matter, returns (None, full_text)."""
    if not text.startswith("---\n"):
        return None, text
    idx = text.find("\n---\n", 4)
    if idx == -1:
        return None, text
    fm = text[4:idx]
    body = text[idx + len("\n---\n"):]
    return fm, body


def _parse_front_matter(path: Path, text: str) -> Dict[str, Any]:
    fm, _ = _split_front_matter(text)
    if fm is None:
        raise VerificationError(f"{path}: missing YAML front matter")
    data = yaml.safe_load(fm) or {}
    if not isinstance(data, dict):
        raise VerificationError(f"{path}: front matter must be a mapping")
    return data


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


def _require_traceability(
    path: Path, front_matter: Dict[str, Any], exempt_files: set
) -> None:
    rel = str(path.relative_to(REPO_ROOT))
    if rel in exempt_files:
        return

    verified_at = front_matter.get("verified_at")
    if not isinstance(verified_at, (str, dt.date)):
        raise VerificationError(
            f"{rel}: missing required front matter field 'verified_at'"
        )

    trace_urls = _collect_traceability_urls(front_matter)
    if not trace_urls:
        raise VerificationError(
            f"{rel}: must include 'source_url' or 'sources' in front matter"
        )

    bad: List[str] = []
    for u in trace_urls:
        host = normalize_host(u)
        if host is None:
            bad.append(u)
    if bad:
        raise VerificationError(f"{rel}: invalid traceability URL(s): {bad}")


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _is_example_url(url: str) -> bool:
    from ..url_utils import is_example_url
    return is_example_url(url)


def extract_content_node(state: VerificationState) -> dict:
    """Node 1: parse markdown files, validate traceability, extract URLs."""
    exceptions = state["exceptions"]
    exempt_traceability_files = {str(p) for p in exceptions["exempt_traceability_files"]}

    md_files = _iter_markdown_files()
    if not md_files:
        return {
            "errors": ["No markdown files found in-scope (_pages/, _posts/)."],
            "file_results": {},
            "all_urls": [],
            "markdown_files": [],
        }

    file_results: Dict[str, dict] = {}
    all_urls_set: set = set()
    errors: List[str] = []

    for path in md_files:
        rel = str(path.relative_to(REPO_ROOT))
        raw = path.read_text(encoding="utf-8")
        front: Dict[str, Any] = {}
        file_errs: List[str] = []

        try:
            front = _parse_front_matter(path, raw)
            _require_traceability(path, front, exempt_traceability_files)
        except Exception as e:
            file_errs.append(str(e))

        _, body = _split_front_matter(raw)
        body_urls = extract_urls_from_text(body)
        trace_urls = _collect_traceability_urls(front) if front else []
        all_urls = sorted(set(trace_urls + body_urls))

        # Collect reachability targets (skip example URLs)
        for u in all_urls:
            host = normalize_host(u)
            if host is None:
                continue
            if _is_example_url(u):
                continue
            all_urls_set.add(u)

        if file_errs:
            errors.extend(file_errs)

        file_results[rel] = {
            "sha256": _sha256_bytes(raw.encode("utf-8")),
            "front_matter": {
                "has_source_url": bool(
                    isinstance(front.get("source_url"), str)
                    and front.get("source_url", "").strip()
                )
                if front
                else False,
                "has_sources": bool(
                    isinstance(front.get("sources"), list)
                    and len(front.get("sources") or []) > 0
                )
                if front
                else False,
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
            "ok": len(file_errs) == 0,
        }

    return {
        "file_results": file_results,
        "all_urls": sorted(all_urls_set),
        "markdown_files": [str(p) for p in md_files],
        "errors": errors,
    }
