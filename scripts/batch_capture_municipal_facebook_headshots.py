#!/usr/bin/env python3
"""Capture municipal candidate Facebook headshots via the live Firefox session."""

from __future__ import annotations

import json
import re
import subprocess
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, urlencode, urlparse, urlunparse

from PIL import Image


LL_ROOT = Path("/Users/sweeden/ll")
CANDIDATES_DIR = LL_ROOT / "_candidates"
DOSSIERS_DIR = Path("/Users/sweeden/research_paper/dossiers/municipal")
REPORT_PATH = LL_ROOT / "_data" / "municipal_facebook_headshot_report.json"
FIREFOX_APP = "/Applications/Firefox.app"

FACEBOOK_SEARCH_PATTERN = re.compile(r"https://www\.facebook\.com/search/top\?q=[^\s)]+")
SEARCH_SUFFIX = "killeen central texas"

# Calibrated against the real Firefox window in the active desktop session.
CLICK_X = 647
CLICK_Y = 314
WINDOW_RECT = (0, 0, 1496, 967)
CROP_RECT = (54, 454, 220, 620)


def municipal_candidate_slugs() -> list[str]:
    """Return dossier slugs that also exist as ll candidate markdown files."""
    dossier_slugs = {
        entry.name
        for entry in DOSSIERS_DIR.iterdir()
        if entry.is_dir() and entry.name != "(vacant)"
    }
    candidate_slugs = {
        path.stem
        for path in CANDIDATES_DIR.glob("*.md")
        if path.name not in {"index.md", "candidates.css", "candidates.yml", "texas_candidates.csv"}
    }
    return sorted(dossier_slugs & candidate_slugs)


def candidate_search_url(slug: str) -> str:
    """Extract and normalize the Facebook search URL for a candidate slug."""
    path = CANDIDATES_DIR / f"{slug}.md"
    text = path.read_text(encoding="utf-8")
    match = FACEBOOK_SEARCH_PATTERN.search(text)
    if not match:
        raise ValueError(f"No Facebook search URL found in {path}")
    return append_search_suffix(match.group(0), SEARCH_SUFFIX)


def append_search_suffix(url: str, suffix: str) -> str:
    """Append the location suffix to the Facebook search query."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    raw_search = query.get("q", [""])[0].replace("+", " ")
    normalized_search = " ".join(part for part in [raw_search.strip(), suffix.strip()] if part)
    query["q"] = [normalized_search]
    encoded_query = urlencode(query, doseq=True, quote_via=quote_plus)
    return urlunparse(parsed._replace(query=encoded_query))


def run_cmd(args: list[str]) -> None:
    """Run a shell command and raise on failure."""
    subprocess.run(args, check=True)


def activate_firefox_with_url(url: str) -> None:
    """Open a URL in the live Firefox app and bring it to the foreground."""
    run_cmd(["open", "-a", FIREFOX_APP, url])
    run_cmd(["osascript", "-e", 'tell application "Firefox" to activate'])


def click_calibrated_point() -> None:
    """Click the calibrated point for the first visible search result."""
    swift = (
        "import CoreGraphics; import Foundation; "
        f"let p = CGPoint(x: {CLICK_X}, y: {CLICK_Y}); "
        "let move = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: p, mouseButton: .left)!; "
        "move.post(tap: .cghidEventTap); "
        "usleep(150000); "
        "let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: p, mouseButton: .left)!; "
        "down.post(tap: .cghidEventTap); "
        "usleep(90000); "
        "let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: p, mouseButton: .left)!; "
        "up.post(tap: .cghidEventTap);"
    )
    run_cmd(["swift", "-e", swift])


def screenshot_png() -> bytes:
    """Take a full-window screenshot and return the bytes."""
    temp_path = Path("/tmp/municipal_facebook_headshot.png")
    if temp_path.exists():
        temp_path.unlink()
    x, y, w, h = WINDOW_RECT
    run_cmd(["screencapture", "-R{x},{y},{w},{h}".format(x=x, y=y, w=w, h=h), str(temp_path)])
    data = temp_path.read_bytes()
    temp_path.unlink(missing_ok=True)
    return data


def crop_headshot(image_bytes: bytes, output_path: Path) -> None:
    """Crop the visible profile avatar area and save it as JPEG."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    cropped = image.crop(CROP_RECT)
    cropped.save(output_path, format="JPEG", quality=92)


def current_firefox_url() -> str:
    """Read the URL from the front Firefox tab."""
    script = 'tell application "Firefox" to get URL of active tab of front window'
    result = subprocess.run(
        ["osascript", "-e", script],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def process_candidate(slug: str) -> dict[str, str | bool]:
    """Open the candidate search, click the first result, and save the cropped headshot."""
    search_url = candidate_search_url(slug)
    activate_firefox_with_url(search_url)
    time.sleep(5)
    click_calibrated_point()
    time.sleep(4)
    image_bytes = screenshot_png()
    output_path = DOSSIERS_DIR / slug / "headshot.jpg"
    crop_headshot(image_bytes, output_path)
    final_url = current_firefox_url()
    return {
        "success": True,
        "search_url": search_url,
        "final_url": final_url,
        "output_path": str(output_path),
    }


def main() -> None:
    """Run the calibrated capture workflow across all municipal dossier candidates."""
    report: dict[str, dict[str, str | bool]] = {}
    slugs = municipal_candidate_slugs()
    print(f"Processing {len(slugs)} municipal candidates with facebook links.")

    for slug in slugs:
        print(f"Processing {slug}...")
        try:
            report[slug] = process_candidate(slug)
        except Exception as exc:
            report[slug] = {
                "success": False,
                "error": str(exc),
            }
            print(f"Failed for {slug}: {exc}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    successes = sum(1 for item in report.values() if item.get("success"))
    print(f"Completed {successes}/{len(slugs)} candidates. Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
