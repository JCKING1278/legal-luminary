#!/usr/bin/env python3
"""
Render compact JSON “group cards” for the candidates roster.

Each card corresponds to one `office` group and includes:
- `office`
- `office_up_for_election_this_year`
- `incumbent` {name, headshot_url}
- `opponents_platform` {key_facts: [..]}

The goal is to support an “inline_text response” use-case where the caller
can embed this JSON directly.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import yaml


LL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_YAML = LL_ROOT / "_candidates" / "candidates.yml"


def _safe_str(val: Any) -> str:
    return "" if val is None else str(val)


def _is_incumbent(candidate: Dict[str, Any]) -> bool:
    return _safe_str(candidate.get("status")).strip().lower() == "incumbent"


def _load_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected YAML structure in {path}")
    return data


def render_cards(input_yaml: Path, *, max_facts: int) -> List[Dict[str, Any]]:
    data = _load_yaml(input_yaml)
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError(f"Expected top-level `candidates: [...]` in {input_yaml}")

    by_office: Dict[str, List[Dict[str, Any]]] = {}
    for c in candidates:
        office = _safe_str(c.get("office")).strip() or "UnknownOffice"
        by_office.setdefault(office, []).append(c)

    cards: List[Dict[str, Any]] = []
    for office, group in by_office.items():
        # Office up-for-election is already computed in YAML; compute defensively as max.
        office_up = any(bool(c.get("office_up_for_election_this_year")) for c in group)

        incumbent = next((c for c in group if _is_incumbent(c)), group[0])
        inc_name = _safe_str(incumbent.get("name")).strip()
        headshot_url = incumbent.get("headshot_url")

        # Same facts list should be shared across candidates in a given office.
        facts = incumbent.get("office_opponents_platform_key_facts") or []
        if not isinstance(facts, list):
            facts = []

        cards.append(
            {
                "office": office,
                "office_up_for_election_this_year": office_up,
                "incumbent": {"name": inc_name, "headshot_url": headshot_url},
                "opponents_platform": {"key_facts": facts[:max_facts]},
            }
        )

    # Deterministic ordering: stable sort by `office` string.
    cards.sort(key=lambda x: x.get("office", ""))
    return cards


def main() -> None:
    parser = argparse.ArgumentParser(description="Render office group cards as JSON.")
    parser.add_argument("--input-yaml", type=Path, default=DEFAULT_INPUT_YAML)
    parser.add_argument("--max-facts", type=int, default=3)
    args = parser.parse_args()

    cards = render_cards(args.input_yaml, max_facts=args.max_facts)
    # Print JSON only (no extra logging) so this is easy to embed.
    print(json.dumps(cards, ensure_ascii=False))


if __name__ == "__main__":
    main()

