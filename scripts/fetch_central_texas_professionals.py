#!/usr/bin/env python3
"""
Fetch random Central Texas notaries and TDLR licensees for the legal-luminary site.

Writes JSON to stdout or to a file. Use for Jekyll _data/central_texas_professionals.json.

  python scripts/fetch_central_texas_professionals.py
  python scripts/fetch_central_texas_professionals.py -o /path/to/legal-luminary/_data/central_texas_professionals.json

Requires: requests, and legal-luminary services on PYTHONPATH (run from legal-luminary dir).
"""

import argparse
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Fetch Central Texas notaries and TDLR licensees")
    parser.add_argument("-o", "--output", help="Output JSON file path (default: stdout)")
    parser.add_argument("--notaries", type=int, default=3, help="Max notaries to include")
    parser.add_argument("--tdlr", type=int, default=3, help="Max TDLR licensees to include")
    args = parser.parse_args()

    # Add parent so we can import services
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from services.tdlr_lookup import random_central_texas_professionals
    except ImportError as e:
        sys.stderr.write(f"Import error: {e}. Run from legal-luminary directory or set PYTHONPATH.\n")
        sys.exit(1)

    try:
        app_token = os.environ.get("SOCRATA_APP_TOKEN")
        data = random_central_texas_professionals(
            notary_limit=args.notaries,
            tdlr_limit=args.tdlr,
            app_token=app_token,
        )
    except Exception as e:
        sys.stderr.write(f"Fetch error: {e}\n")
        sys.exit(1)

    out = json.dumps(data, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
