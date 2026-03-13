#!/usr/bin/env python3
"""
Search a web page for repeating digits (Aho-Corasick) and optionally open in Cursor browser.

Usage:
  python scripts/search_webpage_repeating_digits.py <url>   # fetch URL, print matches
  python scripts/search_webpage_repeating_digits.py          # use Cursor browser (run from agent)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Project root
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from lib.aho_corasick_phone import search_text


def extract_text_from_html(html: str) -> str:
    """Crude strip of HTML tags for text extraction."""
    text = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[^>]*>[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_page_text(url: str) -> str:
    from urllib.request import urlopen
    from urllib.error import URLError

    with urlopen(url, timeout=10) as resp:
        html = resp.read().decode(errors="replace")
    return extract_text_from_html(html)


def run_search(text: str, min_run: int = 2, max_run: int = 2) -> None:
    matches = search_text(text, min_run=min_run, max_run=max_run, context_chars=50)
    if not matches:
        print("No repeating digits found.")
        return
    print(f"Found {len(matches)} repeating digit run(s):\n")
    for end_pos, digit, run, snippet in matches:
        print(f"  '{run}' (digit '{digit}') at position {end_pos}")
        print(f"    context: …{snippet}…")
        print()


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "--snapshot":
        # Read Cursor browser snapshot from stdin
        snapshot = sys.stdin.read()
        run_on_snapshot_yaml(snapshot)
        return 0
    if len(sys.argv) < 2:
        print("Usage: search_webpage_repeating_digits.py <url>", file=sys.stderr)
        print("       search_webpage_repeating_digits.py --snapshot  # read snapshot YAML from stdin", file=sys.stderr)
        return 1
    url = sys.argv[1]
    try:
        text = fetch_page_text(url)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}", file=sys.stderr)
        return 1
    print(f"Searching: {url} ({len(text)} chars)\n")
    run_search(text)
    return 0


def run_on_snapshot_yaml(snapshot_text: str) -> None:
    """Extract text from Cursor browser accessibility snapshot (YAML) and search."""
    names = re.findall(r"name:\s*(.+)", snapshot_text)
    text = " ".join(n.strip() for n in names if n.strip())
    print(f"Extracted {len(text)} chars from snapshot\n")
    run_search(text)


if __name__ == "__main__":
    sys.exit(main())
