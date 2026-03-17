#!/usr/bin/env python3
"""
Fix post dates using date_aware_crawler.extract_date().

Reads each post in _posts, extracts the actual article date from the body
and source_url (same logic as date_aware_crawler), and if it differs from
the front matter date, updates the front matter and renames the file to
YYYY-MM-DD-slug.md.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LL_ROOT = SCRIPT_DIR.parent
POSTS_DIR = LL_ROOT / "_posts"
AGENT_SRC = LL_ROOT.parent / "CS5374_Software_VV" / "project" / "src"

if not AGENT_SRC.is_dir():
    AGENT_SRC = Path(__file__).resolve().parent.parent.parent / "CS5374_Software_VV" / "project" / "src"


def _ensure_agent_path():
    if str(AGENT_SRC) not in sys.path:
        sys.path.insert(0, str(AGENT_SRC))


def extract_date_from_crawler(content: str, url: str) -> str:
    _ensure_agent_path()
    from agent.date_aware_crawler import extract_date
    return extract_date(content or "", url or "")


def parse_post(path: Path) -> tuple[dict, str]:
    """Return (front_matter_dict, body). Front matter is parsed line-by-line for date/source_url."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip().startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm_block = parts[1].strip()
    body = parts[2].strip()
    fm = {}
    for line in fm_block.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body


def slug_from_filename(name: str) -> str:
    """e.g. 2026-03-15-my-slug.md -> my-slug"""
    if name.endswith(".md"):
        name = name[:-3]
    if re.match(r"^\d{4}-\d{2}-\d{2}-", name):
        return name[11:]
    return name


def write_post(path: Path, fm: dict, body: str) -> None:
    """Write front matter and body back to path."""
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not POSTS_DIR.exists():
        print(f"Posts dir not found: {POSTS_DIR}")
        return 1

    fixed = 0
    for path in sorted(POSTS_DIR.glob("*.md")):
        fm, body = parse_post(path)
        current_date = fm.get("date", "").strip()
        source_url = fm.get("source_url", "").strip()
        if not source_url or not current_date:
            continue
        # Extract actual date from article content (same as date_aware_crawler)
        real_date = extract_date_from_crawler(body, source_url)
        if real_date == current_date:
            continue
        # Do not apply crawler default (2026-02-19) when URL/content don't contain that date
        if real_date == "2026-02-19" and "/2026/02/19/" not in source_url and "February 19" not in body and "Feb 19" not in body:
            continue
        # Update front matter
        fm["date"] = real_date
        fm["verified_at"] = real_date
        # Update "Published" and "Verified" in body if present
        body = re.sub(r"\*\*Published\*\*: \S+", f"**Published**: {real_date}", body)
        body = re.sub(r"\*\*Verified\*\*: \S+", f"**Verified**: {real_date}", body)
        write_post(path, fm, body)
        slug = slug_from_filename(path.name)
        new_name = f"{real_date}-{slug}.md"
        new_path = path.parent / new_name
        if new_path != path and not new_path.exists():
            path.rename(new_path)
            print(f"  {path.name} -> {new_name} (date {current_date} -> {real_date})")
        else:
            print(f"  Updated date {current_date} -> {real_date}: {path.name}")
        fixed += 1

    print(f"\nFixed {fixed} post(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
