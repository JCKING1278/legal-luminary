#!/usr/bin/env python3
"""
Fetch RSS feeds from _data/rss-feeds.yml and publish only entirely new articles
to _posts. Does not modify existing posts. Also fetches upcoming events (Texas
Legislature committee meetings) and writes _data/upcoming_events.json.

Sources: ll/_data/rss-feeds.yml, ll/_data/texas_multi_source_data.json (reference),
ll/_data/openclaw-setup.md (upcoming events schema). Bell County school events
come from openclaw-bell-county-calendars.sh when run; this script fills
Legislature upcoming events from RSS.
"""

from __future__ import annotations

import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

# Paths relative to repo root (script in scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
LL_ROOT = SCRIPT_DIR.parent
DATA_DIR = LL_ROOT / "_data"
POSTS_DIR = LL_ROOT / "_posts"
RSS_FEEDS_YML = DATA_DIR / "rss-feeds.yml"
UPCOMING_EVENTS_JSON = DATA_DIR / "upcoming_events.json"

# Namespaces for Atom feeds
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def _fetch_url(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "LegalLuminaryRSS/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _parse_rss_item(item: ET.Element) -> dict[str, Any] | None:
    """Extract title, link, date, excerpt from RSS 2.0 <item>."""
    def text(el: ET.Element | None, tag: str, default: str = "") -> str:
        if el is None:
            return default
        child = el.find(tag)
        return (child.text or "").strip() if child is not None else default

    title = text(item, "title") or text(item, "dc:title")
    link = text(item, "link")
    if not link and item.find("guid") is not None:
        link = text(item, "guid")
    if not title or not link:
        return None
    pub = text(item, "pubDate") or text(item, "dc:date") or text(item, "date")
    desc = text(item, "description") or text(item, "content:encoded") or ""
    # Strip HTML for excerpt
    desc = re.sub(r"<[^>]+>", " ", desc).strip()
    desc = re.sub(r"\s+", " ", desc)[:350]
    return {"title": title, "link": link, "date_raw": pub, "excerpt": desc}


def _parse_atom_entry(entry: ET.Element) -> dict[str, Any] | None:
    """Extract title, link, date, excerpt from Atom <entry>."""
    title_el = entry.find("atom:title", ATOM_NS) or entry.find("title")
    title = (title_el.text or "").strip() if title_el is not None else ""
    link_el = entry.find("atom:link", ATOM_NS) or entry.find("link")
    link = ""
    if link_el is not None:
        link = (link_el.get("href") or "").strip()
    if not title or not link:
        return None
    updated_el = entry.find("atom:updated", ATOM_NS) or entry.find("updated") or entry.find("published")
    date_raw = (updated_el.text or "").strip() if updated_el is not None else ""
    summary_el = entry.find("atom:summary", ATOM_NS) or entry.find("summary") or entry.find("content")
    excerpt = ""
    if summary_el is not None and summary_el.text:
        excerpt = re.sub(r"<[^>]+>", " ", summary_el.text).strip()[:350]
    elif summary_el is not None and len(summary_el):
        excerpt = "".join(summary_el.itertext()).strip()[:350]
    return {"title": title, "link": link, "date_raw": date_raw, "excerpt": excerpt}


def _normalize_date(date_raw: str) -> str:
    """Return YYYY-MM-DD. Tolerate ISO and RSS formats."""
    if not date_raw:
        return datetime.now().strftime("%Y-%m-%d")
    date_raw = date_raw.strip()
    # ISO style: 2026-02-12T06:30:19+00:00 or 2026-02-12
    if "T" in date_raw:
        try:
            return date_raw.split("T")[0][:10]
        except IndexError:
            pass
    if re.match(r"^\d{4}-\d{2}-\d{2}", date_raw):
        return date_raw[:10]
    # RFC 2822 / RSS pubDate
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m/%d/%y",
    ):
        try:
            s = date_raw.replace("Z", "+00:00").rstrip("Z")[:19].strip()
            return datetime.strptime(s, fmt.replace(" %z", "").strip()).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return datetime.now().strftime("%Y-%m-%d")


def parse_feed(url: str, source_name: str, timeout: int = 12) -> list[dict[str, Any]]:
    """Fetch feed URL and return list of {title, link, date, excerpt, source}."""
    raw = _fetch_url(url, timeout=timeout)
    root = ET.fromstring(raw)
    items: list[dict[str, Any]] = []

    # RSS 2.0
    channel = root.find("channel")
    if channel is not None:
        for item in channel.findall("item"):
            parsed = _parse_rss_item(item)
            if parsed:
                parsed["date"] = _normalize_date(parsed["date_raw"])
                parsed["source"] = source_name
                items.append(parsed)
        return items

    # Atom
    if root.tag == "{http://www.w3.org/2005/Atom}feed" or root.tag == "feed":
        for entry in root.findall("atom:entry", ATOM_NS) or root.findall("entry"):
            parsed = _parse_atom_entry(entry)
            if parsed:
                parsed["date"] = _normalize_date(parsed["date_raw"])
                parsed["source"] = source_name
                items.append(parsed)
    return items


def existing_source_urls(posts_dir: Path) -> set[str]:
    """Set of source_url values already used in _posts (normalized)."""
    urls: set[str] = set()
    for path in posts_dir.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"source_url:\s*(\S+)", text):
                url = m.group(1).strip()
                if url.startswith("http"):
                    urls.add(url.rstrip("/"))
        except Exception:
            continue
    return urls


def slug_from_title(title: str, max_len: int = 45) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:max_len] if len(s) > max_len else s


def write_new_post(post_path: Path, item: dict[str, Any]) -> None:
    """Write one new Jekyll post. Does not overwrite."""
    if post_path.exists():
        return
    date = item.get("date") or datetime.now().strftime("%Y-%m-%d")
    title = item["title"]
    link = item["link"]
    source = item["source"]
    excerpt = (item.get("excerpt") or "")[:250].replace('"', '\\"').replace("\n", " ")
    body = (item.get("excerpt") or "").strip()
    post_content = f"""---
category: news
date: {date}
excerpt: "{excerpt}..."
layout: default
news_excerpt: true
source_name: {source}
source_url: {link}
title: {title}
verified_at: {date}
---

{body}

## Source Information

- **Source**: {source}
- **Original URL**: {link}
- **Published**: {date}
- **Verified**: {date}

---
"""
    post_path.write_text(post_content, encoding="utf-8")
    print(f"  New post: {post_path.name}")


def load_feeds_config() -> list[dict[str, Any]]:
    if not yaml or not RSS_FEEDS_YML.exists():
        return []
    data = yaml.safe_load(RSS_FEEDS_YML.read_text(encoding="utf-8"))
    feeds = data.get("feeds") or []
    return [f for f in feeds if f.get("enabled") is True]


def main() -> int:
    if not RSS_FEEDS_YML.exists():
        print(f"Config not found: {RSS_FEEDS_YML}")
        return 1
    config = load_feeds_config()
    if not config:
        print("No enabled feeds in rss-feeds.yml")
        return 0

    existing = existing_source_urls(POSTS_DIR)
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    new_count = 0

    # Separate upcoming-events feeds (Legislature committee meetings) from article feeds
    article_feeds = []
    upcoming_feeds = []
    for f in config:
        name = (f.get("name") or "").lower()
        if "upcoming" in name and ("committee" in name or "meeting" in name):
            upcoming_feeds.append(f)
        else:
            article_feeds.append(f)

    print("=== New articles from RSS (no changes to existing posts) ===\n")
    for feed_config in article_feeds:
        name = feed_config.get("name", "Unknown")
        url = feed_config.get("url", "")
        max_items = int(feed_config.get("max_items") or 10)
        if not url:
            continue
        try:
            items = parse_feed(url, name)
        except Exception as e:
            print(f"  Skip {name}: {e}")
            continue
        for item in items[:max_items]:
            link = (item["link"] or "").rstrip("/")
            if link in existing:
                continue
            date = item["date"] or datetime.now().strftime("%Y-%m-%d")
            slug = slug_from_title(item["title"])
            if not slug:
                slug = "untitled"
            post_path = POSTS_DIR / f"{date}-{slug}.md"
            if post_path.exists():
                existing.add(link)
                continue
            write_new_post(post_path, item)
            existing.add(link)
            new_count += 1
        if items:
            print(f"  {name}: {len(items)} items")

    print(f"\nTotal new articles written: {new_count}")

    # Upcoming events: fetch Legislature committee meetings and write _data/upcoming_events.json
    print("\n=== Upcoming events (Texas Legislature) ===")
    legislature_events: list[dict[str, Any]] = []
    for feed_config in upcoming_feeds:
        name = feed_config.get("name", "Unknown")
        url = feed_config.get("url", "")
        max_items = int(feed_config.get("max_items") or 10)
        if not url:
            continue
        try:
            items = parse_feed(url, name)
        except Exception as e:
            print(f"  Skip {name}: {e}")
            continue
        for item in items[:max_items]:
            legislature_events.append({
                "title": item["title"],
                "url": item["link"],
                "date": item["date"],
                "source": name,
            })
        print(f"  {name}: {len(items)} upcoming items")

    # Merge with existing upcoming_events.json (keep districts if present)
    output: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "week_start": "",
        "week_end": "",
        "source_index_url": "https://www.bellcountytx.com/about_us/school_districts/index.php",
        "districts": [],
        "legislature_upcoming": legislature_events,
    }
    if UPCOMING_EVENTS_JSON.exists():
        try:
            import json
            existing_data = json.loads(UPCOMING_EVENTS_JSON.read_text(encoding="utf-8"))
            output["districts"] = existing_data.get("districts", [])
            output["week_start"] = existing_data.get("week_start", "")
            output["week_end"] = existing_data.get("week_end", "")
        except Exception:
            pass
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    import json
    UPCOMING_EVENTS_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"  Wrote {UPCOMING_EVENTS_JSON.name} ({len(legislature_events)} Legislature events)")

    # One new "Upcoming events" summary post if we have events and don't already have a recent one
    if legislature_events:
        today = datetime.now().strftime("%Y-%m-%d")
        summary_slug = "upcoming-texas-legislature-committee-meetings"
        summary_path = POSTS_DIR / f"{today}-{summary_slug}.md"
        if not summary_path.exists():
            lines = [f"- **{e['date']}** – [{e['title'][:60]}]({e['url']}) ({e['source']})" for e in legislature_events[:15]]
            summary_body = "Upcoming Texas Legislature committee meetings (from official RSS feeds):\n\n" + "\n".join(lines)
            summary_post = f"""---
category: news
date: {today}
excerpt: "Upcoming Texas Legislature House and Senate committee meetings."
layout: default
news_excerpt: true
source_name: Texas Legislature
source_url: https://capitol.texas.gov
title: Upcoming Texas Legislature committee meetings
verified_at: {today}
---

{summary_body}

## Source

- **Source**: Texas Legislature (capitol.texas.gov)
- **Data**: _data/upcoming_events.json (legislature_upcoming)
---
"""
            summary_path.write_text(summary_post, encoding="utf-8")
            print(f"  New summary post: {summary_path.name}")
            new_count += 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
