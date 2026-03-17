#!/usr/bin/env python3
"""
Run the Texas news crawl and publish pipeline using agent modules from
CS5374_Software_VV/project/src/agent.

Uses sources from:
- date_aware_crawler (Texas Tribune, KWTX, KBTX, KXAN, KVUE, KCEN, KXXV, KWKT,
  Killeen Daily Herald, Temple Daily Telegram, Belton Journal, Fort Hood Sentinel,
  Salado Village Voice, KTEM News)
- ll/_data/news-feed.json and allowlist (demos/langsmith_langgraph_demo/allowlist.json)
  for domain allowlist

Pipeline order (per agent docs):
  1. date_aware_crawler  → writes new Jekyll posts to ll/_posts
  2. cleanup_summarize   → cleans/complete truncated posts in _posts
  3. evidence_validator → scores and writes ll/_data/important_articles.json
  4. aho_corasick_automaton_ranker → updates important_articles.json with AC ranking

Optional: Run Node texas_data_crawler.js and texas_data_pipeline.py to refresh
Texas dataset discovery (data.texas.gov); they do not write articles to _posts.

Usage:
  # From repo root (ll)
  LEGAL_LUMINARY_POSTS=$PWD/_posts LEGAL_LUMINARY_DATA=$PWD/_data python scripts/run_texas_crawl_and_publish.py

  # Skip crawl (only cleanup + validate + rank existing posts)
  SKIP_CRAWL=1 python scripts/run_texas_crawl_and_publish.py

  # Crawl only one source
  CRAWL_ONLY_SOURCE="Texas Tribune" python scripts/run_texas_crawl_and_publish.py
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Resolve ll repo root and agent src (sibling project)
SCRIPT_DIR = Path(__file__).resolve().parent
LL_ROOT = SCRIPT_DIR.parent
AGENT_SRC = LL_ROOT.parent / "CS5374_Software_VV" / "project" / "src"
if not AGENT_SRC.is_dir():
    AGENT_SRC = Path(os.environ.get("AGENT_SRC", "")).resolve()
if not AGENT_SRC.is_dir():
    print("Agent source not found. Set AGENT_SRC or place CS5374_Software_VV next to ll.", file=sys.stderr)
    sys.exit(1)

POSTS_DIR = LL_ROOT / "_posts"
DATA_DIR = LL_ROOT / "_data"
ALLOWLIST_CANDIDATE = LL_ROOT / "demos" / "langsmith_langgraph_demo" / "allowlist.json"


def _env_setup() -> None:
    os.environ.setdefault("LEGAL_LUMINARY_POSTS", str(POSTS_DIR))
    os.environ.setdefault("LEGAL_LUMINARY_DATA", str(DATA_DIR))
    if ALLOWLIST_CANDIDATE.exists():
        os.environ.setdefault("LEGAL_LUMINARY_ALLOWLIST", str(ALLOWLIST_CANDIDATE))
    # So evidence_validator includes only newly modified posts in important_articles when desired
    os.environ.setdefault("LEGAL_LUMINARY_NEW_ONLY", "1")
    os.environ.setdefault("NEW_ARTICLES_DAYS", "2")


def _run_crawl() -> bool:
    if os.environ.get("SKIP_CRAWL", "").strip().lower() in ("1", "true", "yes"):
        print("Skipping crawl (SKIP_CRAWL=1).")
        return True
    sys.path.insert(0, str(AGENT_SRC))
    try:
        from agent.date_aware_crawler import main as crawl_main
        print("=== Phase 1: Date-aware news crawl ===")
        asyncio.run(crawl_main())
        return True
    except ImportError as e:
        print(f"Crawl skipped (import error): {e}", file=sys.stderr)
        return False
    finally:
        if str(AGENT_SRC) in sys.path:
            sys.path.remove(str(AGENT_SRC))


def _run_cleanup() -> bool:
    sys.path.insert(0, str(AGENT_SRC))
    try:
        from agent.cleanup_summarize import main as cleanup_main
        print("\n=== Phase 2: Cleanup and summarize ===")
        cleanup_main()
        return True
    except ImportError as e:
        print(f"Cleanup skipped (import error): {e}", file=sys.stderr)
        return False
    finally:
        if str(AGENT_SRC) in sys.path:
            sys.path.remove(str(AGENT_SRC))


def _run_evidence_validator() -> bool:
    sys.path.insert(0, str(AGENT_SRC))
    try:
        from agent.evidence_validator import main as validator_main
        print("\n=== Phase 3: Evidence validator (priority scoring) ===")
        validator_main()
        return True
    except ImportError as e:
        print(f"Validator skipped (import error): {e}", file=sys.stderr)
        return False
    finally:
        if str(AGENT_SRC) in sys.path:
            sys.path.remove(str(AGENT_SRC))


def _run_aho_corasick_ranker() -> bool:
    sys.path.insert(0, str(AGENT_SRC))
    try:
        from agent.aho_corasick_automaton_ranker import main as ranker_main
        print("\n=== Phase 4: Aho-Corasick ranker ===")
        ranker_main()
        return True
    except ImportError as e:
        print(f"Ranker skipped (import error): {e}", file=sys.stderr)
        return False
    finally:
        if str(AGENT_SRC) in sys.path:
            sys.path.remove(str(AGENT_SRC))


def main() -> int:
    parser = argparse.ArgumentParser(description="Crawl Texas sources and publish to ll/_posts")
    parser.add_argument("--skip-crawl", action="store_true", help="Skip date_aware_crawler")
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip cleanup_summarize")
    parser.add_argument("--skip-validator", action="store_true", help="Skip evidence_validator")
    parser.add_argument("--skip-ranker", action="store_true", help="Skip aho_corasick_automaton_ranker")
    args = parser.parse_args()

    if args.skip_crawl:
        os.environ["SKIP_CRAWL"] = "1"

    _env_setup()
    print(f"Posts: {os.environ['LEGAL_LUMINARY_POSTS']}")
    print(f"Data:  {os.environ['LEGAL_LUMINARY_DATA']}")
    print()

    ok = True
    if not args.skip_crawl:
        ok = _run_crawl() and ok
    if not args.skip_cleanup:
        ok = _run_cleanup() and ok
    if not args.skip_validator:
        ok = _run_evidence_validator() and ok
    if not args.skip_ranker:
        ok = _run_aho_corasick_ranker() and ok

    print("\n=== Done ===")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
