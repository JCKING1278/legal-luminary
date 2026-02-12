#!/usr/bin/env python3
"""
Texas Notary Public finder — search by name or city.

Data: Texas Notary Public Commissions (Texas Open Data Portal)
https://data.texas.gov/dataset/Texas-Notary-Public-Commissions/gmd3-bnrd

Usage:
  python run_notary_finder.py "Smith"
  python run_notary_finder.py --last "Garcia" --city "Austin" --limit 20
  python run_notary_finder.py --first "Kathy" --last "Lapham"
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Search Texas Notary Public Commissions by name or city."
    )
    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Free-text search (name, address, etc.)",
    )
    parser.add_argument("--first", "-f", help="First name (contains)")
    parser.add_argument("--last", "-l", help="Last name (contains)")
    parser.add_argument("--city", "-c", help="City (searched in address)")
    parser.add_argument("--limit", "-n", type=int, default=25, help="Max results (default 25)")
    parser.add_argument("--id", dest="notary_id", help="Look up by notary commission ID")
    args = parser.parse_args()

    # Run from legal-luminary so config and services resolve
    cwd = os.path.dirname(os.path.abspath(__file__))
    if os.getcwd() != cwd:
        os.chdir(cwd)
    sys.path.insert(0, cwd)

    from services.notary_finder import NotaryFinder, search_notaries

    if args.notary_id:
        try:
            from config.settings import (
                SOCRATA_APP_TOKEN,
                TEXAS_NOTARY_DATASET_ID,
                TEXAS_SODA_BASE,
            )
            finder = NotaryFinder(
                base_url=TEXAS_SODA_BASE,
                dataset_id=TEXAS_NOTARY_DATASET_ID,
                app_token=SOCRATA_APP_TOKEN or None,
            )
        except ImportError:
            finder = NotaryFinder()
        rec = finder.get_by_id(args.notary_id)
        if not rec:
            print(f"No notary found with ID: {args.notary_id}")
            sys.exit(1)
        print(f"Notary ID: {rec.notary_id}")
        print(f"Name: {rec.full_name()}")
        print(f"Effective: {rec.effective_date}  Expires: {rec.expire_date}")
        print(f"Address: {rec.address}")
        print(f"Email: {rec.email_address}")
        print(f"Surety: {rec.surety_company}")
        print(f"Agency: {rec.agency}")
        return

    results = search_notaries(
        query=args.query,
        first_name=args.first,
        last_name=args.last,
        city=args.city,
        limit=args.limit,
    )
    if not results:
        print("No notaries found.")
        sys.exit(0)
    print(f"Found {len(results)} notary/notaries:\n")
    for r in results:
        print(f"  {r.full_name()}  (ID: {r.notary_id})")
        print(f"    {r.address}")
        print(f"    Expires: {r.expire_date}")
        print()


if __name__ == "__main__":
    main()
