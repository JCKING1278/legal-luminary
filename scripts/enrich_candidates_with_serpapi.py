#!/usr/bin/env python3
"""
Enrich candidates YAML with grouping/tagging metadata and (optionally) SerpApi-derived
factual snippets (headshot/avatar + opponents platform facts + largest financial supporter).

Design goals:
- Deterministic grouping/up-for-election/incumbent detection even when SerpApi is disabled.
- SerpApi calls only happen when an API key is available (env: SERPAPI_API_KEY) or via
  --serpapi-api-key CLI flag.
- SerpApi results are cached on disk to avoid re-querying.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import httpx
import yaml


LL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_YAML = LL_ROOT / "_candidates" / "candidates.yml"
DEFAULT_MIRROR_YAML = LL_ROOT / "_data" / "candidates.yml"

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


ELECTION_PHASES_UP_FOR_ELECTION = {"primary_2026", "runoff_2026", "general_2026"}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _coerce_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        return val.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _safe_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val)


def _extract_group_city_state_function(candidate: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Best-effort heuristic mapping from current YAML fields to:
    - group_city
    - group_state
    - group_function
    """

    position = _safe_str(candidate.get("position"))
    office = _safe_str(candidate.get("office"))
    jurisdiction = _safe_str(candidate.get("jurisdiction"))

    # State: this dataset is Central Texas.
    group_state = "Texas" if ("TX" in office or "Texas" in position or "Texas" in jurisdiction) else "Texas"

    # City: try to find "City of <X>" patterns, otherwise search for known city names in position/office.
    group_city = ""
    m = re.search(r"City of\s+([A-Za-z][A-Za-z\s-]+)", position, flags=re.IGNORECASE)
    if m:
        group_city = m.group(1).strip()
    else:
        # Common cities present in the roster.
        for city in ["Killeen", "Temple", "Belton", "Austin", "Waco"]:
            if re.search(rf"\b{re.escape(city)}\b", position, flags=re.IGNORECASE) or re.search(
                rf"\b{re.escape(city)}\b", office, flags=re.IGNORECASE
            ):
                group_city = city
                break

    office_lower = f"{office} {position}".lower()

    # Function mapping: broad buckets suitable for UI grouping.
    if "mayor" in office_lower or "sheriff" in office_lower:
        group_function = "Executive"
    elif "council" in office_lower or "representative" in office_lower or "senator" in office_lower:
        group_function = "Legislative"
    elif "justice of the peace" in office_lower or "judge" in office_lower:
        group_function = "Judicial"
    elif "board" in office_lower or "education" in office_lower or "cte" in office_lower:
        group_function = "Education"
    elif "commissioner" in office_lower:
        group_function = "CountyAdministration"
    else:
        # Fallback: keep it stable, not empty.
        group_function = "Government"

    return group_city, group_state, group_function


def _is_incumbent(candidate: Dict[str, Any]) -> bool:
    status = _safe_str(candidate.get("status")).strip().lower()
    return status == "incumbent"


def _election_phase_up_for_office(candidate: Dict[str, Any]) -> bool:
    phase = _safe_str(candidate.get("election_phase")).strip()
    return phase in ELECTION_PHASES_UP_FOR_ELECTION


def _office_sort_key(
    candidate: Dict[str, Any],
    *,
    office: str,
    group_city: str,
    group_function: str,
) -> Tuple[str, str, str, int]:
    # Candidate ordering should keep incumbents first within the same office group.
    incumbent_first = 0 if _is_incumbent(candidate) else 1
    # Keep original numeric id order as stable secondary sort.
    cand_id = candidate.get("id")
    try:
        cand_id_int = int(cand_id)
    except Exception:
        cand_id_int = 10**9
    return (group_city or "", group_function or "", office or "", incumbent_first * 10_000 + cand_id_int)


def _extract_answer_key_facts(serpapi_payload: Dict[str, Any], *, max_facts: int = 3) -> List[str]:
    """
    Pull short textual facts from a SerpApi response in a defensive way.
    """

    facts: List[str] = []

    # 1) Answer box / knowledge graph often contains a short summary.
    for key in ["answer_box", "knowledge_graph", "featured_snippet"]:
        if key in serpapi_payload and isinstance(serpapi_payload[key], dict):
            txt = serpapi_payload[key].get("snippet") or serpapi_payload[key].get("description") or ""
            txt = _safe_str(txt).strip()
            if txt:
                facts.append(txt)

    # 2) Organic snippets as fallback.
    organic = serpapi_payload.get("organic_results") or []
    if isinstance(organic, list):
        for r in organic:
            if len(facts) >= max_facts:
                break
            if not isinstance(r, dict):
                continue
            snippet = _safe_str(r.get("snippet")).strip()
            if snippet and snippet not in facts:
                # Keep snippet short for JSON cards.
                snippet = snippet.replace("\n", " ").strip()
                if len(snippet) > 260:
                    snippet = snippet[:257].rstrip() + "..."
                facts.append(snippet)

    # Deduplicate while preserving order.
    seen = set()
    deduped: List[str] = []
    for f in facts:
        if f not in seen:
            seen.add(f)
            deduped.append(f)
    return deduped[:max_facts]


def _extract_supporter_name_and_work_for(snippet: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Best-effort parsing of a supporter snippet into (name, work_for).
    SerpApi snippets are not standardized, so this is intentionally conservative.
    """
    s = (snippet or "").strip().replace("\n", " ")
    if not s:
        return None, None

    # Common pattern: "Person Name, who works for Employer ..."
    m = re.search(
        r"^(?P<name>[^.,;]+?)(?:,)?\s*(?:who\s+)?works\s+for\s+(?P<work>[^.]+)",
        s,
        flags=re.IGNORECASE,
    )
    if m:
        name = m.group("name").strip()
        work = m.group("work").strip()
        return name or None, work or None

    # Common pattern: "Person Name at Employer ..."
    m = re.search(
        r"^(?P<name>[^.,;]+?)(?:,)?\s+at\s+(?P<work>[^.]+)",
        s,
        flags=re.IGNORECASE,
    )
    if m:
        name = m.group("name").strip()
        work = m.group("work").strip()
        return name or None, work or None

    return None, None


@dataclass(frozen=True)
class SerpApiConfig:
    api_key: str
    cache_dir: Path
    http_timeout_s: int = 30


class SerpApiClient:
    def __init__(self, cfg: SerpApiConfig):
        self._cfg = cfg
        self._client = httpx.Client(timeout=cfg.http_timeout_s)

    def _cache_path(self, *, engine: str, query: str, extra: Dict[str, Any]) -> Path:
        key_obj = {"engine": engine, "query": query, "extra": extra}
        key = _sha256_text(json.dumps(key_obj, sort_keys=True, ensure_ascii=True))
        return self._cfg.cache_dir / f"{engine}_{key}.json"

    def _get_cached_or_query(self, *, engine: str, query: str, extra: Dict[str, Any]) -> Dict[str, Any]:
        self._cfg.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = self._cache_path(engine=engine, query=query, extra=extra)
        if cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8"))

        params = {
            "engine": engine,
            "q": query,
            "api_key": self._cfg.api_key,
        }
        params.update(extra)

        resp = self._client.get(SERPAPI_ENDPOINT, params=params)
        resp.raise_for_status()
        payload = resp.json()
        cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    def google_search_key_facts(self, query: str, *, max_facts: int = 3) -> List[str]:
        payload = self._get_cached_or_query(engine="google", query=query, extra={})
        return _extract_answer_key_facts(payload, max_facts=max_facts)

    def google_images_headshot_url(self, query: str) -> Optional[str]:
        """
        Pull a best-guess headshot URL from image results.
        """
        payload = self._get_cached_or_query(engine="google_images", query=query, extra={"tbm": "isch"})
        images = payload.get("images_results") or []
        if not isinstance(images, list) or not images:
            return None
        first = images[0] if isinstance(images[0], dict) else {}
        # SerpApi varies; try a few common keys.
        for k in ["original", "original_image", "image", "thumbnail", "url"]:
            url = first.get(k)
            if url:
                return str(url)
        return None

    def google_search_top_links(self, query: str, *, max_links: int = 3) -> List[str]:
        """
        Return top organic result links for a query.
        """
        payload = self._get_cached_or_query(engine="google", query=query, extra={})
        results = payload.get("organic_results") or []
        links: List[str] = []
        if not isinstance(results, list):
            return links
        for r in results:
            if len(links) >= max_links:
                break
            if not isinstance(r, dict):
                continue
            link = r.get("link") or r.get("url")
            if link:
                links.append(str(link))
        return links

    def google_search_top_link(self, query: str) -> Optional[str]:
        links = self.google_search_top_links(query, max_links=1)
        return links[0] if links else None


def _candidate_city_for_social(candidate: Dict[str, Any], fallback: str = "Central Texas") -> str:
    """
    Prefer the deterministically derived `group_city`, but fall back to Central Texas.
    """
    city = _safe_str(candidate.get("group_city")).strip()
    return city or fallback


def _load_yaml(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected YAML structure in {path}")
    return data


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
    # Preserve insertion order: PyYAML 6+ supports sort_keys.
    text = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=False,
    )
    path.write_text(text, encoding="utf-8")


def _compute_office_groups(candidates: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for c in candidates:
        office = _safe_str(c.get("office")).strip()
        if not office:
            office = "UnknownOffice"
        groups.setdefault(office, []).append(c)
    return groups


def _pick_office_incumbent_name(office_group: List[Dict[str, Any]]) -> str:
    for c in office_group:
        if _is_incumbent(c):
            return _safe_str(c.get("name")).strip()
    return _safe_str(office_group[0].get("name")).strip() if office_group else ""


def _pick_office_opponents_names(office_group: List[Dict[str, Any]]) -> List[str]:
    inc = None
    for c in office_group:
        if _is_incumbent(c):
            inc = _safe_str(c.get("name")).strip()
            break
    opponents: List[str] = []
    for c in office_group:
        name = _safe_str(c.get("name")).strip()
        if not name:
            continue
        if inc and name == inc:
            continue
        opponents.append(name)
    return opponents


def enrich_candidates(
    *,
    input_yaml: Path,
    mirror_yaml: Path,
    skip_serpapi: bool,
    serpapi_api_key: Optional[str],
    cache_dir: Path,
) -> None:
    data = _load_yaml(input_yaml)
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError(f"Expected top-level `candidates: [...]` in {input_yaml}")

    # Compute group-level fields first.
    office_groups = _compute_office_groups(candidates)

    # Precompute group city/state/function for every candidate deterministically.
    for c in candidates:
        group_city, group_state, group_function = _extract_group_city_state_function(c)
        c["group_city"] = group_city
        c["group_state"] = group_state
        c["group_function"] = group_function
        c["office_group_key"] = _safe_str(c.get("office")).strip() or "UnknownOffice"

    # Office-level metadata.
    office_up: Dict[str, bool] = {}
    office_incumbent: Dict[str, str] = {}
    office_opponents_platform_facts: Dict[str, List[str]] = {}
    office_headshot_url: Dict[str, Optional[str]] = {}

    for office, group in office_groups.items():
        office_up[office] = any(_election_phase_up_for_office(c) for c in group)
        office_incumbent[office] = _pick_office_incumbent_name(group)

        # Placeholders for UI fields.
        office_opponents_platform_facts[office] = []
        office_headshot_url[office] = None

    # Enrich via SerpApi if enabled.
    serp: Optional[SerpApiClient] = None
    if not skip_serpapi:
        key = serpapi_api_key or os.environ.get("SERPAPI_API_KEY", "").strip()
        if not key:
            print("[warn] SERPAPI_API_KEY missing; skipping SerpApi enrichment.")
        else:
            serp = SerpApiClient(
                SerpApiConfig(
                    api_key=key,
                    cache_dir=cache_dir,
                )
            )

    if serp is not None:
        for office, group in office_groups.items():
            incumb = office_incumbent[office]
            opponents = _pick_office_opponents_names(group)

            # Headshot URL: prefer incumbent portrait.
            headshot_query = f"{incumb} headshot official portrait"
            office_headshot_url[office] = serp.google_images_headshot_url(headshot_query)

            # Opponents platform facts: limit opponent list to a handful to keep query short.
            opponents_for_query = opponents[:5]
            opponents_blob = ", ".join(opponents_for_query) if opponents_for_query else "opponents"
            platform_query = (
                f"{office} election. Key platform issues for candidates: {opponents_blob}. "
                f"Provide a short factual summary."
            )
            office_opponents_platform_facts[office] = serp.google_search_key_facts(
                platform_query, max_facts=3
            )

    # Largest financial supporter (FEC yes candidates only).
    # Note: the existing CSV doesn't contain donor identity; we rely on SerpApi to find
    # the “biggest supporter” as requested.
    for c in candidates:
        office = _safe_str(c.get("office")).strip() or "UnknownOffice"
        c["office_up_for_election_this_year"] = office_up.get(office, False)
        c["office_incumbent_name"] = office_incumbent.get(office, "")
        # Copy the list object so PyYAML doesn't emit YAML anchors/references.
        c["office_opponents_platform_key_facts"] = list(
            office_opponents_platform_facts.get(office, [])
        )
        c["headshot_url"] = office_headshot_url.get(office)

        # Supporter fields default.
        c["largest_financial_supporter_name"] = None
        c["largest_financial_supporter_work_for"] = None

        fec = _safe_str(c.get("FEC")).strip().lower()
        if serp is not None and fec == "yes":
            cand_name = _safe_str(c.get("name")).strip()
            office_title = _safe_str(c.get("office")).strip()
            supporter_query = (
                f"Who is the largest donor or financial supporter of {cand_name} for {office_title}? "
                f"Include who that supporter works for."
            )
            facts = serp.google_search_key_facts(supporter_query, max_facts=1)
            if facts:
                snippet = facts[0]
                name, work_for = _extract_supporter_name_and_work_for(snippet)
                c["largest_financial_supporter_name"] = name or snippet
                c["largest_financial_supporter_work_for"] = work_for

    # Social URLs for every candidate (independent of FEC flag).
    if serp is not None:
        for c in candidates:
            name = _safe_str(c.get("name")).strip()
            office = _safe_str(c.get("office")).strip()
            city = _candidate_city_for_social(c)

            c.setdefault("facebook_url", None)
            c.setdefault("instagram_url", None)
            c.setdefault("linkedin_url", None)

            if not c.get("facebook_url"):
                fb_query = f'{name} "{office}" "{city}" Facebook'
                c["facebook_url"] = serp.google_search_top_link(fb_query)

            if not c.get("instagram_url"):
                ig_query = f'{name} "{office}" "{city}" Instagram'
                c["instagram_url"] = serp.google_search_top_link(ig_query)

            if not c.get("linkedin_url"):
                li_query = f'{name} "{office}" "{city}" LinkedIn'
                c["linkedin_url"] = serp.google_search_top_link(li_query)

    # Reorder candidates to cluster by opponent/office and show incumbents first.
    def sort_key(c: Dict[str, Any]) -> Tuple[str, str, str, int]:
        office = _safe_str(c.get("office")).strip() or "UnknownOffice"
        group_city = _safe_str(c.get("group_city")).strip()
        group_function = _safe_str(c.get("group_function")).strip()
        return _office_sort_key(c, office=office, group_city=group_city, group_function=group_function)

    candidates_sorted = sorted(candidates, key=sort_key)
    data["candidates"] = candidates_sorted

    # Mirror update.
    _dump_yaml(input_yaml, data)

    mirror_data = _load_yaml(mirror_yaml)
    mirror_data["candidates"] = candidates_sorted
    if "metadata" in mirror_data and "metadata" in data:
        mirror_data["metadata"] = data.get("metadata")
    _dump_yaml(mirror_yaml, mirror_data)

    print(f"[ok] Updated {input_yaml} and mirrored to {mirror_yaml}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich candidate YAML with grouping + SerpApi.")
    parser.add_argument("--input-yaml", type=Path, default=DEFAULT_INPUT_YAML)
    parser.add_argument("--mirror-yaml", type=Path, default=DEFAULT_MIRROR_YAML)
    parser.add_argument("--skip-serpapi", action="store_true", help="Update YAML without any SerpApi calls.")
    parser.add_argument("--serpapi-api-key", type=str, default="", help="Optional SerpApi key override.")
    parser.add_argument("--cache-dir", type=Path, default=LL_ROOT / ".cache" / "serpapi_candidates")

    args = parser.parse_args()

    enrich_candidates(
        input_yaml=args.input_yaml,
        mirror_yaml=args.mirror_yaml,
        skip_serpapi=args.skip_serpapi,
        serpapi_api_key=args.serpapi_api_key or None,
        cache_dir=args.cache_dir,
    )


if __name__ == "__main__":
    main()

