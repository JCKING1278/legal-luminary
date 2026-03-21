#!/usr/bin/env python3
"""
Print only the rows for Texas (TX) candidates from `_candidates/candidate_summary_2026.csv`.

Outputs CSV to stdout (includes the header row).
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
LL_ROOT = SCRIPT_DIR.parent
DEFAULT_INPUT = LL_ROOT / "_candidates" / "candidate_summary_2026.csv"
STATE_FIELD = "Cand_State"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print TX rows from candidate_summary_2026.csv to stdout."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Path to candidate CSV (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--state",
        default="TX",
        help="Two-letter state code to filter (default: TX)",
    )
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise SystemExit("Error: CSV has no header row.")
        if STATE_FIELD not in reader.fieldnames:
            raise SystemExit(
                f"Error: expected state field {STATE_FIELD!r}; found: {reader.fieldnames}"
            )

        writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
        writer.writeheader()

        target = (args.state or "").strip().upper()
        try:
            for row in reader:
                if (row.get(STATE_FIELD) or "").strip().upper() == target:
                    writer.writerow(row)
        except BrokenPipeError:
            # Allow piping to commands like `head` without noisy tracebacks.
            try:
                sys.stdout.close()
            except Exception:
                pass
            return


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
