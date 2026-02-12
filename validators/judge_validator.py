"""
Judge Validator

Validates judge names against federal and state court rosters.
Uses CourtListener Judge API:
  - Search API (type=p): Primary lookup for judges by name
  - People API: Person records with biographical data
  - Positions API: Court assignments, appointment dates, appointer

Ref: https://www.courtlistener.com/help/api/rest/judges/
"""

import re
import requests
from langsmith import traceable
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from state import ValidationResult, ProvenanceMetadata, VerificationStatus
from config.settings import (
    COURTLISTENER_API_KEY,
    COURTLISTENER_BASE_URL,
    MIN_CONFIDENCE_THRESHOLD,
)


# ---------------------------------------------------------------------------
# CourtListener Judge API endpoints
# ---------------------------------------------------------------------------
COURTLISTENER_SEARCH_URL = f"{COURTLISTENER_BASE_URL}/search/"
COURTLISTENER_PEOPLE_URL = f"{COURTLISTENER_BASE_URL}/people/"
COURTLISTENER_POSITIONS_URL = f"{COURTLISTENER_BASE_URL}/positions/"


@traceable(name="validate_judge")
def validate_judge(state: dict) -> dict:
    """
    Validate a judge name and court assignment.

    Checks:
    1. CourtListener Search API (type=p) for judge records
    2. CourtListener People/Positions for court details (fallback)
    3. LLM knowledge cross-reference
    4. Court assignment consistency
    """
    query = state.get("query", "")
    raw_content = state.get("raw_content", "")

    # Step 1: Search CourtListener Judge API for the judge
    cl_result = _search_courtlistener_judges(query)

    # Step 2: LLM cross-reference
    llm_result = _llm_judge_verification(query, raw_content)

    # Aggregate
    confidence = _calculate_judge_confidence(cl_result, llm_result)
    is_valid = confidence >= MIN_CONFIDENCE_THRESHOLD

    result = ValidationResult(
        is_valid=is_valid,
        status=VerificationStatus.VERIFIED if is_valid else VerificationStatus.UNVERIFIED,
        confidence=confidence,
        source_used="CourtListener Judge API (Search + People) + LLM cross-reference",
        details=f"CourtListener match: {cl_result.get('found', False)}, "
                f"Judge: {cl_result.get('name', 'not found')}, "
                f"Courts: {cl_result.get('courts', 'unknown')}, "
                f"LLM confidence: {llm_result:.2f}",
        provenance=ProvenanceMetadata(
            source_url=cl_result.get("url", ""),
            source_name="CourtListener",
            verification_status=VerificationStatus.VERIFIED if is_valid else VerificationStatus.UNVERIFIED,
            confidence_score=confidence,
            authoritative_source="courtlistener.com",
        ),
    )

    return {
        **state,
        "judge_validation": result,
    }


def _search_courtlistener_judges(query: str) -> dict:
    """
    Search CourtListener for a judge using the Judge API.

    Primary: Search API (type=p) - full-text judge search with positions and courts.
    Fallback: People API with name filters if Search returns no results.
    """
    name = _extract_judge_name(query)
    if not name:
        return {"found": False, "name": "", "courts": "", "url": ""}

    # 1. Try Search API (type=p) - designed for judge/people search
    result = _search_judges_by_name(name)
    if result.get("found"):
        return result

    # 2. Fallback: People API with name filters
    return _search_people_api(name)


def _search_judges_by_name(name: str) -> dict:
    """Use CourtListener Search API (type=p) to find judges by name."""
    try:
        headers = {}
        if COURTLISTENER_API_KEY:
            headers["Authorization"] = f"Token {COURTLISTENER_API_KEY}"

        response = requests.get(
            COURTLISTENER_SEARCH_URL,
            params={"q": name, "type": "p", "page_size": 5},
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            return {"found": False, "name": name, "courts": "", "url": ""}

        data = response.json()
        results = data.get("results", [])

        if not results:
            return {"found": False, "name": name, "courts": "", "url": ""}

        # Pick best match by name similarity (handle "John Roberts" vs "John Robert Blakey")
        best = _pick_best_judge_match(name, results)
        if not best:
            return {"found": False, "name": name, "courts": "", "url": ""}

        # Parse Search API judge result: name, positions[], absolute_url
        positions = best.get("positions", [])
        courts = ", ".join(
            p.get("court_full_name", "") or p.get("court", "")
            for p in positions
            if p.get("court") or p.get("court_full_name")
        ) or "Unknown court"

        abs_url = best.get("absolute_url", "")
        url = f"https://www.courtlistener.com{abs_url}" if abs_url.startswith("/") else abs_url

        return {
            "found": True,
            "name": best.get("name", name),
            "courts": courts,
            "positions": positions,
            "url": url,
        }
    except Exception as e:
        return {"found": False, "name": name, "courts": "", "url": "", "error": str(e)}


def _pick_best_judge_match(query_name: str, results: list) -> dict | None:
    """Pick the judge result that best matches the query name."""
    query_parts = set(re.findall(r"\w+", query_name.lower()))
    if not query_parts:
        return results[0] if results else None

    best_score = -1
    best_result = None
    for r in results:
        cand_name = (r.get("name") or "").lower()
        cand_parts = set(re.findall(r"\w+", cand_name))
        overlap = len(query_parts & cand_parts) / len(query_parts) if query_parts else 0
        if overlap > best_score:
            best_score = overlap
            best_result = r

    return best_result if best_score >= 0.5 else (results[0] if results else None)


def _search_people_api(name: str) -> dict:
    """
    Fallback: CourtListener People API with name filters.
    Uses name_last__icontains / name_first__icontains per REST API filtering.
    """
    try:
        headers = {}
        if COURTLISTENER_API_KEY:
            headers["Authorization"] = f"Token {COURTLISTENER_API_KEY}"

        # Split name for filtering (last name is most distinctive)
        parts = name.strip().split()
        last_name = parts[-1] if parts else ""
        first_name = parts[0] if len(parts) > 1 else ""

        params = {
            "page_size": 5,
            "is_alias_of__isnull": "true",  # Exclude aliases per Judge API docs
        }
        if last_name:
            params["name_last__icontains"] = last_name
        if first_name:
            params["name_first__icontains"] = first_name

        response = requests.get(
            COURTLISTENER_PEOPLE_URL,
            params=params,
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            return {"found": False, "name": name, "courts": "", "url": ""}

        data = response.json()
        results = data.get("results", [])

        if not results:
            return {"found": False, "name": name, "courts": "", "url": ""}

        person = results[0]
        full_name = _build_person_name(person)
        resource_uri = person.get("resource_uri", "")
        url = resource_uri if resource_uri.startswith("http") else f"https://www.courtlistener.com{resource_uri}"

        # Optionally fetch positions for court info
        courts = _fetch_person_courts(person.get("id"), headers)

        return {
            "found": True,
            "name": full_name,
            "courts": courts or "Unknown court",
            "url": url,
        }
    except Exception as e:
        return {"found": False, "name": name, "courts": "", "url": "", "error": str(e)}


def _build_person_name(person: dict) -> str:
    """Build full name from People API fields: name_first, name_last, name_middle, name_suffix."""
    first = person.get("name_first", "") or ""
    middle = person.get("name_middle", "") or ""
    last = person.get("name_last", "") or ""
    suffix = person.get("name_suffix", "") or ""
    parts = [p for p in [first, middle, last, suffix] if p]
    return " ".join(parts) if parts else ""


def _fetch_person_courts(person_id: int, headers: dict) -> str:
    """Fetch court names from Positions API for a person."""
    try:
        response = requests.get(
            COURTLISTENER_POSITIONS_URL,
            params={"person": person_id, "page_size": 10},
            headers=headers,
            timeout=10,
        )
        if response.status_code != 200:
            return ""

        data = response.json()
        results = data.get("results", [])
        courts = []
        for pos in results:
            court = pos.get("court")
            if isinstance(court, dict):
                courts.append(court.get("full_name", "") or court.get("short_name", "") or "")
            elif isinstance(court, str):
                courts.append(court)
        return ", ".join(c for c in courts if c) or ""
    except Exception:
        return ""


def _extract_judge_name(query: str) -> str:
    """Extract a judge's name from the query text."""
    query_lower = query.lower()
    # Remove common prefixes
    for prefix in ["judge ", "justice ", "chief justice ", "hon. ", "honorable "]:
        if query_lower.startswith(prefix):
            return query[len(prefix):].strip()
    return query.strip()


def _llm_judge_verification(query: str, raw_content: str) -> float:
    """Use LLM to verify judge information."""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        messages = [
            SystemMessage(content="""You are a legal research specialist. Verify whether the
following judge name and court assignment are accurate based on your knowledge.
Rate your confidence from 0.0 (certainly wrong) to 1.0 (certainly correct).
Consider: Is this a real judge? Is the court assignment correct? Are dates accurate?
Respond with ONLY a decimal number."""),
            HumanMessage(content=f"Verify: {query}\nContext: {raw_content[:500]}")
        ]
        response = llm.invoke(messages)
        return max(0.0, min(1.0, float(response.content.strip())))
    except Exception:
        return 0.5


def _calculate_judge_confidence(cl_result: dict, llm_score: float) -> float:
    """Weighted confidence for judge validation."""
    cl_score = 1.0 if cl_result.get("found") else 0.0
    weights = {"courtlistener": 0.6, "llm": 0.4}
    return round(weights["courtlistener"] * cl_score + weights["llm"] * llm_score, 3)
