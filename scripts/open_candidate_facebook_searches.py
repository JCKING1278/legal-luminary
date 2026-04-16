#!/usr/bin/env python3
"""Open all candidate Facebook searches in Firefox tabs."""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, urlencode, urlparse, urlunparse

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions


CANDIDATES_DIR = Path("/Users/sweeden/ll/_candidates")
SEARCH_SUFFIX = "killeen central texas"
FIREFOX_BINARY = Path("/Applications/Firefox.app/Contents/MacOS/firefox")
FIREFOX_APP = Path("/Applications/Firefox.app")
FIREFOX_PROFILE = Path("/Users/sweeden/Library/Application Support/Firefox/Profiles/0zx9leie.default-release")
FACEBOOK_SEARCH_PATTERN = re.compile(r"https://www\.facebook\.com/search/top\?q=[^\s)]+")


def extract_candidate_links() -> list[str]:
    """Collect Facebook search links from all candidate markdown files."""
    links: list[str] = []
    for path in sorted(CANDIDATES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = FACEBOOK_SEARCH_PATTERN.search(text)
        if match:
            links.append(append_search_suffix(match.group(0), SEARCH_SUFFIX))
    return links


def append_search_suffix(url: str, suffix: str) -> str:
    """Append a location suffix to the Facebook search query."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    raw_search = query.get("q", [""])[0].replace("+", " ")
    normalized_search = " ".join(part for part in [raw_search.strip(), suffix.strip()] if part)
    query["q"] = [normalized_search]
    encoded_query = urlencode(query, doseq=True, quote_via=quote_plus)
    return urlunparse(parsed._replace(query=encoded_query))


def open_links_in_firefox(urls: list[str]) -> None:
    """Open each URL in a Firefox tab and keep the session alive."""
    if not urls:
        raise SystemExit("No Facebook candidate search links were found.")

    if firefox_is_running():
        for url in urls:
            subprocess.run(
                ["open", "-a", str(FIREFOX_APP), url],
                check=True,
            )
        print(f"Opened {len(urls)} Facebook candidate search tabs in the running Firefox profile.")
        return

    options = FirefoxOptions()
    options.binary_location = str(FIREFOX_BINARY)
    options.add_argument("-profile")
    options.add_argument(str(FIREFOX_PROFILE))
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(urls[0])
        for url in urls[1:]:
            driver.switch_to.new_window("tab")
            driver.get(url)

        print(f"Opened {len(urls)} Facebook candidate search tabs in Firefox.")
        print("Firefox will stay open until this process is stopped.")
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Stopping Firefox session.")
    finally:
        driver.quit()


def firefox_is_running() -> bool:
    """Return whether Firefox is already running for the current user."""
    result = subprocess.run(
        ["pgrep", "-x", "firefox"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


if __name__ == "__main__":
    open_links_in_firefox(extract_candidate_links())
