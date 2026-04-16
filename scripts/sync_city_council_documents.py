#!/usr/bin/env python3
"""
Download city council agendas/minutes PDFs for Bell County area cities listed in
`_data/city_council_document_sources.json`, then scan text for names from each city's
`_cities/<slug>/README.md` roster tables (heuristic).

Usage (from repo root `ll/`):
  uv run python scripts/sync_city_council_documents.py --all
  uv run python scripts/sync_city_council_documents.py --city killeen temple

Requires: httpx (project dependency). Optional: pypdf for PDF text extraction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, unquote, urlparse

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "_data" / "city_council_document_sources.json"
DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 municipal-sync/0.1"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_roster_names(readme_path: Path) -> list[str]:
    if not readme_path.is_file():
        return []
    text = readme_path.read_text(encoding="utf-8", errors="replace")
    names: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        parts = [p.strip() for p in s.split("|")]
        parts = [p for p in parts if p and not re.match(r"^-+$", p)]
        if len(parts) < 2:
            continue
        if parts[0].lower() in ("position", "---") or parts[0] == "---":
            continue
        # Header: | Position | Name | or | Position | Name | District |
        if parts[0].lower() == "position" and parts[1].lower() in ("name", "district"):
            continue
        if len(parts) >= 3 and parts[1].lower() == "name":
            continue
        # Data: | Mayor | Riakos Adams |  OR  | Mayor | Tim Davis | At-Large |
        if len(parts) >= 3 and re.search(r"\s", parts[1]):
            candidate = parts[1]
        else:
            candidate = parts[-1]
        if candidate in ("-", "Vacant") or candidate.lower() in ("name", "district", "term expires"):
            continue
        if candidate.startswith("("):
            continue
        if re.search(r"[A-Za-z]", candidate):
            names.append(candidate)
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for n in names:
        key = n.casefold()
        if key not in seen:
            seen.add(key)
            out.append(n)
    return out


def _href_urls(html: str, base: str) -> list[str]:
    found: list[str] = []
    for m in re.finditer(r'href\s*=\s*"([^"]+)"', html, re.I):
        href = m.group(1).strip()
        if href.startswith("#") or href.lower().startswith("javascript:"):
            continue
        abs_url = urljoin(base, href)
        found.append(abs_url)
    for m in re.finditer(r"href\s*=\s*'([^']+)'", html, re.I):
        href = m.group(1).strip()
        abs_url = urljoin(base, href)
        found.append(abs_url)
    return found


def _filter_urls(
    urls: list[str],
    include: re.Pattern[str] | None,
    exclude: re.Pattern[str] | None,
) -> list[str]:
    out: list[str] = []
    for u in urls:
        dec = unquote(u)
        if include and not include.search(dec) and not include.search(u):
            continue
        if exclude and (exclude.search(dec) or exclude.search(u)):
            continue
        out.append(u)
    return out


def _temple_archive_sort_key(url: str) -> tuple[int, str]:
    m = re.search(r"archive/city council/(\d{4})/", url, re.I)
    year = int(m.group(1)) if m else 0
    return (year, url)


def collect_legistar_urls(
    client: str,
    body_name: str,
    since: str,
    max_events: int,
    prefer: list[str],
    max_downloads: int,
) -> list[tuple[str, str]]:
    """Return list of (kind, url) for agenda/minutes files."""
    # OData filter
    filt = (
        f"EventBodyName eq '{body_name}' and "
        f"EventDate ge datetime'{since}T00:00:00'"
    )
    api = f"https://webapi.legistar.com/v1/{client}/events"
    params = {
        "$filter": filt,
        "$orderby": "EventDate desc",
        "$top": str(max(1, max_events)),
    }
    out: list[tuple[str, str]] = []
    with httpx.Client(timeout=60.0, headers={"User-Agent": DEFAULT_UA}) as cli:
        r = cli.get(api, params=params)
        r.raise_for_status()
        events = r.json()
    if not isinstance(events, list):
        return out
    for ev in events:
        if prefer:
            if "minutes" in prefer and ev.get("EventMinutesFile"):
                out.append(("minutes", ev["EventMinutesFile"]))
            if "agenda" in prefer and ev.get("EventAgendaFile"):
                out.append(("agenda", ev["EventAgendaFile"]))
        else:
            if ev.get("EventMinutesFile"):
                out.append(("minutes", ev["EventMinutesFile"]))
            if ev.get("EventAgendaFile"):
                out.append(("agenda", ev["EventAgendaFile"]))
    # de-dupe URLs
    seen: set[str] = set()
    deduped: list[tuple[str, str]] = []
    for kind, u in out:
        if u not in seen:
            seen.add(u)
            deduped.append((kind, u))
    return deduped[: max(1, max_downloads)]


def collect_html_pdf_urls(
    seed_urls: list[str],
    include_regex: str | None,
    exclude_regex: str | None,
    max_downloads: int,
    *,
    relative_pdf_base: str | None = None,
    strip_query_parameters: bool = False,
) -> list[str]:
    inc = re.compile(include_regex) if include_regex else None
    exc = re.compile(exclude_regex) if exclude_regex else None
    collected: list[str] = []
    with httpx.Client(timeout=60.0, headers={"User-Agent": DEFAULT_UA}, follow_redirects=True) as cli:
        for seed in seed_urls:
            r = cli.get(seed)
            r.raise_for_status()
            base = relative_pdf_base or str(r.url)
            hrefs = _href_urls(r.text, base)
            pdfs = [u for u in hrefs if ".pdf" in u.lower() or "/page/open/" in u.lower()]
            # Nolanville-style: /page/open/.../file.pdf — treat as fetchable
            fixed = []
            for u in pdfs:
                if "/page/open/" in u.lower() and not u.lower().endswith(".pdf"):
                    continue
                fixed.append(u)
            pdfs = fixed
            matched = _filter_urls(pdfs, inc, exc)
            for u in matched:
                if strip_query_parameters and "?" in u:
                    u = u.split("?", 1)[0]
                if u not in collected:
                    collected.append(u)
    if any("templetx.gov" in u and "archive/city council" in u.lower() for u in collected):
        collected = sorted(collected, key=_temple_archive_sort_key, reverse=True)
    return collected[:max_downloads]


def safe_filename(url: str) -> str:
    path = urlparse(url).path
    name = Path(path).name.split("?")[0] or "document.pdf"
    name = re.sub(r"[^\w.\-]+", "_", unquote(name))[:180]
    h = hashlib.sha256(url.encode()).hexdigest()[:10]
    stem = Path(name).stem
    suf = Path(name).suffix or ".pdf"
    return f"{stem}_{h}{suf}"


def download_file(cli: httpx.Client, url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with cli.stream("GET", url, follow_redirects=True) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with tmp.open("wb") as f:
            for chunk in r.iter_bytes(65536):
                f.write(chunk)
        tmp.rename(dest)


def pdf_to_text(path: Path, max_pages: int = 8) -> str | None:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return None
    try:
        reader = PdfReader(str(path))
        parts: list[str] = []
        for i, page in enumerate(reader.pages[:max_pages]):
            t = page.extract_text() or ""
            if t:
                parts.append(t)
        return "\n".join(parts)
    except Exception:
        return None


def scan_text_for_names(text: str, names: list[str]) -> dict[str, list[str]]:
    """Return up to 3 short snippets per name."""
    hits: dict[str, list[str]] = {}
    if not text:
        return hits
    lines = text.splitlines()
    for name in names:
        variants = [name]
        if " " in name:
            variants.append(name.split()[-1])  # last name
        snippets: list[str] = []
        for i, line in enumerate(lines):
            low = line.lower()
            for v in variants:
                if len(v) < 3:
                    continue
                if v.lower() in low:
                    lo = max(0, i - 1)
                    hi = min(len(lines), i + 3)
                    chunk = " ".join(x.strip() for x in lines[lo:hi] if x.strip())
                    if chunk and chunk not in snippets:
                        snippets.append(chunk[:500])
                if len(snippets) >= 3:
                    break
        if snippets:
            hits[name] = snippets
    return hits


def run_city(
    city: dict[str, Any],
    out_root: Path,
    delay: float,
    client: httpx.Client,
    *,
    text_sample_pdfs: int = 12,
) -> dict[str, Any]:
    slug = city["slug"]
    display = city.get("display_name", slug)
    readme = REPO_ROOT / city.get("readme_path", f"_cities/{slug}/README.md")
    roster = _parse_roster_names(readme)
    dest_dir = out_root / slug
    manifest: dict[str, Any] = {
        "slug": slug,
        "display_name": display,
        "roster_names": roster,
        "downloads": [],
        "errors": [],
    }

    if city.get("manual"):
        manifest["skipped"] = city["manual"]
        return manifest

    src = city["source"]
    stype = src["type"]
    tasks: list[tuple[str, str]] = []

    if stype == "legistar":
        pairs = collect_legistar_urls(
            src["client"],
            src["body_name"],
            src.get("since", "2023-01-01"),
            int(src.get("max_events", 24)),
            [x.lower() for x in src.get("prefer", ["minutes", "agenda"])],
            int(src.get("max_downloads", 40)),
        )
        tasks = pairs
    elif stype == "html_pdf":
        urls = collect_html_pdf_urls(
            src["seed_urls"],
            src.get("include_url_regex"),
            src.get("exclude_url_regex"),
            int(src.get("max_downloads", 20)),
            relative_pdf_base=src.get("relative_pdf_base"),
            strip_query_parameters=bool(src.get("strip_query_parameters")),
        )
        tasks = [("pdf", u) for u in urls]
    else:
        manifest["errors"].append(f"unknown source type: {stype}")
        return manifest

    for kind, url in tasks:
        fname = safe_filename(url)
        target = dest_dir / fname
        if target.is_file():
            manifest["downloads"].append(
                {"url": url, "kind": kind, "path": str(target.relative_to(REPO_ROOT)), "cached": True}
            )
            continue
        try:
            download_file(client, url, target)
            manifest["downloads"].append(
                {"url": url, "kind": kind, "path": str(target.relative_to(REPO_ROOT)), "cached": False}
            )
        except Exception as e:
            manifest["errors"].append({"url": url, "error": str(e)})
        time.sleep(delay)

    # Text scan (sample recent files by mtime)
    pdf_files = sorted(dest_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)[
        :text_sample_pdfs
    ]
    name_hits: dict[str, list[str]] = {}
    for pdf in pdf_files:
        text = pdf_to_text(pdf)
        if not text:
            continue
        h = scan_text_for_names(text, roster)
        for k, v in h.items():
            name_hits.setdefault(k, [])
            for s in v:
                if s not in name_hits[k]:
                    name_hits[k].append(s)
    manifest["name_snippets"] = name_hits
    return manifest


def write_summary_md(results: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Municipal meeting documents sync",
        "",
        "Automated pull of council agendas/minutes where `city_council_document_sources.json` "
        "defines a machine-readable source. Snippets match roster names from each city's "
        "`README.md` (heuristic; verify against original PDFs).",
        "",
    ]
    for m in results:
        lines.append(f"## {m.get('display_name', m['slug'])} (`{m['slug']}`)")
        lines.append("")
        if m.get("skipped"):
            lines.append(f"*Skipped:* {m['skipped']}")
            lines.append("")
            continue
        lines.append(f"- Files saved under `{m['slug']}/` in the meetings cache directory.")
        lines.append(f"- Roster names parsed: {', '.join(m.get('roster_names', [])) or '(none)'}")
        lines.append(f"- Downloaded: {len(m.get('downloads', []))} file(s).")
        if m.get("errors"):
            lines.append(f"- Errors: {len(m['errors'])}")
            for e in m["errors"][:5]:
                lines.append(f"  - `{e.get('url', '')}`: {e.get('error', '')}")
        nh = m.get("name_snippets") or {}
        if nh:
            lines.append("- Name mentions (sampled PDF text):")
            for name, snips in nh.items():
                lines.append(f"  - **{name}**")
                for s in snips[:2]:
                    lines.append(f"    - {s}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=CONFIG_PATH)
    ap.add_argument("--city", nargs="*", help="City slugs (default: all with non-manual sources)")
    ap.add_argument("--all", action="store_true", help="Sync every city entry that has a source block")
    args = ap.parse_args()

    cfg = _load_json(args.config)
    out_root = REPO_ROOT / cfg.get("output_subdir", "_data/meetings_cache")
    delay = float(cfg.get("delay_seconds", 0.5))
    cities: list[dict[str, Any]] = cfg["cities"]

    selected_slugs = set(args.city or [])
    if selected_slugs:
        to_run = [c for c in cities if c["slug"] in selected_slugs]
    elif args.all:
        to_run = list(cities)
    else:
        to_run = [c for c in cities if "source" in c]

    results: list[dict[str, Any]] = []
    with httpx.Client(headers={"User-Agent": DEFAULT_UA}) as cli:
        for city in to_run:
            if "source" not in city:
                results.append(
                    {
                        "slug": city["slug"],
                        "display_name": city.get("display_name", city["slug"]),
                        "skipped": city.get("manual", "no source configured"),
                    }
                )
                continue
            results.append(run_city(city, out_root, delay, cli))

    manifest_path = out_root / "last_sync_manifest.json"
    manifest_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary_md(results, out_root / "incumbent_snippets.md")
    print(f"Wrote {manifest_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {(out_root / 'incumbent_snippets.md').relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
