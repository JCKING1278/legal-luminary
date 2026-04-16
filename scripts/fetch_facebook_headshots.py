#!/usr/bin/env python3
"""Fetch candidate headshots from Facebook search results."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
import time
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, urlencode, urlparse, urlunparse

import requests
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


CANDIDATES_DIR = Path("/Users/sweeden/ll/_candidates")
OUTPUT_BASE = Path("/Users/sweeden/ll/assets/imgs/candidates")
REPORT_PATH = Path("/Users/sweeden/ll/_data/facebook_headshot_fetch_report.json")
FIREFOX_BINARY = Path("/Applications/Firefox.app/Contents/MacOS/firefox")
ACTIVE_PROFILE = Path(
    "/Users/sweeden/Library/Application Support/Firefox/Profiles/0zx9leie.default-release"
)
SEARCH_SUFFIX = "killeen central texas"
FACEBOOK_SEARCH_PATTERN = re.compile(r"https://www\.facebook\.com/search/top\?q=[^\s)]+")
PROFILE_LINK_EXCLUDES = (
    "/search/",
    "/groups/",
    "/events/",
    "/watch/",
    "/marketplace/",
    "/photo/",
    "/photos/",
    "/reel/",
    "/share/",
    "/login/",
)


@dataclass
class CandidateSearch:
    slug: str
    search_url: str
    output_path: Path


def extract_candidate_searches() -> list[CandidateSearch]:
    """Collect all candidate Facebook search URLs from markdown files."""
    searches: list[CandidateSearch] = []
    for path in sorted(CANDIDATES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = FACEBOOK_SEARCH_PATTERN.search(text)
        if not match:
            continue
        searches.append(
            CandidateSearch(
                slug=path.stem,
                search_url=append_search_suffix(match.group(0), SEARCH_SUFFIX),
                output_path=OUTPUT_BASE / path.stem / "headshot.jpg",
            )
        )
    return searches


def append_search_suffix(url: str, suffix: str) -> str:
    """Append a location suffix to the Facebook search query."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    raw_search = query.get("q", [""])[0].replace("+", " ")
    normalized_search = " ".join(part for part in [raw_search.strip(), suffix.strip()] if part)
    query["q"] = [normalized_search]
    encoded_query = urlencode(query, doseq=True, quote_via=quote_plus)
    return urlunparse(parsed._replace(query=encoded_query))


def copy_profile_to_temp() -> Path:
    """Copy the active Firefox profile so Selenium can use it without lock contention."""
    temp_root = Path(tempfile.mkdtemp(prefix="fb-profile-"))
    destination = temp_root / "profile"

    def ignore_files(_: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in {"parent.lock", "lock", ".parentlock", "SingletonLock"}
        }

    shutil.copytree(ACTIVE_PROFILE, destination, ignore=ignore_files, dirs_exist_ok=True)
    return destination


def build_driver(profile_dir: Path) -> webdriver.Firefox:
    """Launch Firefox with a copied user profile."""
    options = FirefoxOptions()
    options.binary_location = str(FIREFOX_BINARY)
    options.add_argument("-profile")
    options.add_argument(str(profile_dir))
    return webdriver.Firefox(options=options)


def collect_profile_links(driver: webdriver.Firefox) -> list[WebElement]:
    """Collect candidate profile-like links from the current Facebook search page."""
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
    time.sleep(3)

    candidates: list[WebElement] = []
    seen: set[str] = set()
    for element in driver.find_elements(By.TAG_NAME, "a"):
        href = (element.get_attribute("href") or "").strip()
        text = (element.text or "").strip()
        aria = (element.get_attribute("aria-label") or "").strip()
        label = text or aria

        if not href.startswith("https://www.facebook.com/"):
            continue
        if any(fragment in href for fragment in PROFILE_LINK_EXCLUDES):
            continue
        if "?" in href and "profile.php" not in href:
            href = href.split("?", 1)[0]
        if href in seen:
            continue
        if not label:
            continue

        seen.add(href)
        candidates.append(element)
    return candidates


def open_first_profile(driver: webdriver.Firefox) -> str:
    """Open the first plausible Facebook profile result and return its URL."""
    links = collect_profile_links(driver)
    if not links:
        raise RuntimeError("No profile-like Facebook search results found.")

    href = links[0].get_attribute("href")
    if not href:
        raise RuntimeError("First Facebook result did not have a usable href.")

    driver.get(href)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(3)
    return driver.current_url


def fetch_image_bytes(driver: webdriver.Firefox) -> bytes:
    """Fetch the best profile image bytes from the current page."""
    meta_url = ""
    try:
        meta = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']")
        meta_url = (meta.get_attribute("content") or "").strip()
    except Exception:
        meta_url = ""

    if meta_url:
        response = requests.get(meta_url, timeout=30)
        response.raise_for_status()
        return response.content

    images = driver.find_elements(By.TAG_NAME, "img")
    for image in images:
        src = (image.get_attribute("src") or "").strip()
        alt = (image.get_attribute("alt") or "").strip().lower()
        width = image.size.get("width", 0)
        height = image.size.get("height", 0)
        if not src.startswith("http"):
            continue
        if width < 120 or height < 120:
            continue
        if "profile" in alt or "photo" in alt or "picture" in alt:
            response = requests.get(src, timeout=30)
            response.raise_for_status()
            return response.content

    raise RuntimeError("No usable profile image found on the selected Facebook page.")


def save_as_jpeg(image_bytes: bytes, output_path: Path) -> None:
    """Save image bytes as a normalized JPEG file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image.save(output_path, format="JPEG", quality=92)


def run() -> None:
    """Run the Facebook headshot fetch workflow across all candidates."""
    searches = extract_candidate_searches()
    profile_dir = copy_profile_to_temp()
    driver = build_driver(profile_dir)
    report: dict[str, dict[str, str | bool]] = {}

    try:
        for item in searches:
            print(f"Processing {item.slug}...")
            try:
                driver.get(item.search_url)
                selected_url = open_first_profile(driver)
                image_bytes = fetch_image_bytes(driver)
                save_as_jpeg(image_bytes, item.output_path)
                report[item.slug] = {
                    "success": True,
                    "search_url": item.search_url,
                    "selected_url": selected_url,
                    "output_path": str(item.output_path),
                }
                print(f"Saved {item.output_path}")
            except TimeoutException as exc:
                report[item.slug] = {
                    "success": False,
                    "search_url": item.search_url,
                    "error": f"timeout: {exc}",
                }
                print(f"Timed out for {item.slug}")
            except Exception as exc:
                report[item.slug] = {
                    "success": False,
                    "search_url": item.search_url,
                    "error": str(exc),
                }
                print(f"Failed for {item.slug}: {exc}")
    finally:
        driver.quit()
        shutil.rmtree(profile_dir.parent, ignore_errors=True)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    successes = sum(1 for entry in report.values() if entry.get("success"))
    print(f"Completed {successes}/{len(searches)} headshots. Report: {REPORT_PATH}")


if __name__ == "__main__":
    run()
