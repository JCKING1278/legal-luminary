#!/usr/bin/env python3
"""
Validate frontmatter confidence scoring for Legal Luminary markdown files.

This script validates that all markdown files have the required:
- Confidence scoring comments
- Frontmatter with sources and confidence metadata
- QFA state tracking

Usage:
    python scripts/validate_frontmatter.py [--fix]
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional

FRONTMATTER_REQUIRED = ["sources", "confidence"]
CONFIDENCE_REQUIRED = ["base", "current", "formula", "qfa_state", "milestone"]
VALID_QFA_STATES = ["INIT", "OBSERVE", "VALIDATE", "INTEGRATE", "REFRESH"]
VALID_MILESTONES = ["M1", "M2", "M3", "M4"]


def parse_frontmatter(content: str) -> Optional[dict]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    frontmatter_text = parts[1]

    try:
        import yaml

        return yaml.safe_load(frontmatter_text)
    except ImportError:
        return parse_simple_yaml(frontmatter_text)


def parse_simple_yaml(text: str) -> dict:
    """Simple YAML parser for basic key-value pairs."""
    result = {}
    for line in text.strip().split("\n"):
        if ":" in line and not line.strip().startswith("#"):
            key, val = line.split(":", 1)
            result[key.strip()] = val.strip().strip("\"'")
    return result


def extract_confidence_comment(content: str) -> Optional[dict]:
    """Extract confidence scoring from HTML comment header."""
    pattern = r"<!--\s*CONFIDENCE SCORE:\s*([0-9.]+).*?-->"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return {"score": float(match.group(1))}
    return None


def validate_file(filepath: Path, fix: bool = False) -> list[str]:
    """Validate a single markdown file."""
    errors = []

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"Cannot read file: {e}")
        return errors

    has_frontmatter = "---" in content[:500]
    has_confidence_comment = "CONFIDENCE SCORE:" in content

    if not has_frontmatter:
        errors.append("Missing frontmatter (file should start with '---')")

    if not has_confidence_comment:
        errors.append("Missing confidence scoring comment header")

    frontmatter = parse_frontmatter(content)
    if frontmatter:
        for field in FRONTMATTER_REQUIRED:
            if field not in frontmatter:
                errors.append(f"Missing frontmatter field: {field}")

        if "confidence" in frontmatter:
            conf = frontmatter["confidence"]
            for field in CONFIDENCE_REQUIRED:
                if field not in conf:
                    errors.append(f"Missing confidence.{field}")

            if "qfa_state" in conf and conf["qfa_state"] not in VALID_QFA_STATES:
                errors.append(f"Invalid QFA state: {conf['qfa_state']}")

            if "milestone" in conf and conf["milestone"] not in VALID_MILESTONES:
                errors.append(f"Invalid milestone: {conf['milestone']}")

            if "base" in conf:
                base = float(conf["base"])
                if not (0.5 <= base <= 0.707):
                    errors.append(f"Base confidence out of range [0.5, 0.707]: {base}")

            if "current" in conf:
                current = float(conf["current"])
                if not (0.0 <= current <= 1.0):
                    errors.append(f"Current confidence out of range [0, 1]: {current}")

        if "sources" in frontmatter:
            sources = frontmatter["sources"]
            if isinstance(sources, list):
                for i, source in enumerate(sources):
                    if isinstance(source, dict):
                        if "url" not in source:
                            errors.append(f"Source {i}: missing 'url'")
                        if "evidence" not in source:
                            errors.append(f"Source {i}: missing 'evidence'")

    return errors


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate frontmatter confidence scoring"
    )
    parser.add_argument("--fix", action="store_true", help="Attempt to fix errors")
    parser.add_argument("--path", default="_pages", help="Path to validate")
    parser.add_argument("--cities", action="store_true", help="Also validate _cities/")
    args = parser.parse_args()

    base_path = Path(__file__).parent.parent
    paths_to_check = [base_path / args.path]

    if args.cities:
        paths_to_check.append(base_path / "_cities")

    all_errors = []

    try:
        from aho_corasick_confidence import AhoCorasickConfidenceTracker

        tracker = AhoCorasickConfidenceTracker()
        use_aho_corasick = True
    except ImportError:
        use_aho_corasick = False
        tracker = None

    milestone_totals = {}

    for path in paths_to_check:
        if not path.exists():
            print(f"Warning: {path} does not exist")
            continue

        print(f"\nValidating {path}...")

        for filepath in path.rglob("*.md"):
            errors = validate_file(filepath, fix=args.fix)

            if use_aho_corasick and tracker:
                try:
                    content = filepath.read_text(encoding="utf-8")
                    analysis = tracker.analyze_file(str(filepath), content)

                    for milestone, boost in analysis.milestone_contributions.items():
                        if milestone not in milestone_totals:
                            milestone_totals[milestone] = 0.0
                        milestone_totals[milestone] += boost
                except Exception:
                    pass

            if errors:
                all_errors.extend([f"{filepath}: {e}" for e in errors])
                print(f"  ✗ {filepath.relative_to(base_path)}")
                for error in errors:
                    print(f"    - {error}")
            else:
                print(f"  ✓ {filepath.relative_to(base_path)}")

    print(f"\n{'=' * 60}")

    if use_aho_corasick and milestone_totals:
        print("\nAho-Corasick Milestone Progress:")
        for milestone, total in sorted(milestone_totals.items()):
            bar = "█" * min(int(total * 50), 50)
            print(f"  {milestone}: {total:.4f} [{bar}]")

    if all_errors:
        print(f"\nFAIL: {len(all_errors)} errors found")
        for error in all_errors:
            print(f"  {error}")
        return 1
    else:
        print("PASS: All files validated successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())
