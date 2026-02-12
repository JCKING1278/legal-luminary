"""
Notary Public Validator

Validates notary public names and lookups against the Texas Notary Public
Commissions dataset (Texas Open Data Portal / Socrata). Data is from the
Office of the Texas Secretary of State.

Dataset: https://data.texas.gov/dataset/Texas-Notary-Public-Commissions/gmd3-bnrd
"""

import re
import sys
import os

from langsmith import traceable

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from state import ValidationResult, ProvenanceMetadata, VerificationStatus
from config.settings import MIN_CONFIDENCE_THRESHOLD

TEXAS_NOTARY_DATASET_URL = (
    "https://data.texas.gov/dataset/Texas-Notary-Public-Commissions/gmd3-bnrd"
)


@traceable(name="validate_notary")
def validate_notary(state: dict) -> dict:
    """
    Validate a notary public name or search query against Texas SOS data.

    Uses the Texas Notary Public Commissions dataset (Socrata). If the query
    matches one or more commissioned notaries, validation passes with confidence
    based on match quality.
    """
    query = (state.get("query", "") or "").strip()
    raw_content = state.get("raw_content", "")

    if not query:
        result = ValidationResult(
            is_valid=False,
            status=VerificationStatus.UNVERIFIED,
            confidence=0.0,
            source_used="Texas Notary Public Commissions (data.texas.gov)",
            details="No query provided for notary lookup.",
            provenance=ProvenanceMetadata(
                source_url=TEXAS_NOTARY_DATASET_URL,
                source_name="Texas Open Data Portal",
                verification_status=VerificationStatus.UNVERIFIED,
                confidence_score=0.0,
                authoritative_source="data.texas.gov",
            ),
        )
        return {**state, "notary_validation": result}

    try:
        from services.notary_finder import search_notaries

        # Treat query as free-text (name or city); optional: parse "City, TX" or "Name"
        results = search_notaries(query=query, limit=20)
    except Exception as e:
        result = ValidationResult(
            is_valid=False,
            status=VerificationStatus.FAILED,
            confidence=0.0,
            source_used="Texas Notary Public Commissions (data.texas.gov)",
            details=f"Notary API error: {e}",
            provenance=ProvenanceMetadata(
                source_url=TEXAS_NOTARY_DATASET_URL,
                source_name="Texas Open Data Portal",
                verification_status=VerificationStatus.FAILED,
                confidence_score=0.0,
                authoritative_source="data.texas.gov",
            ),
        )
        return {**state, "notary_validation": result}

    if not results:
        result = ValidationResult(
            is_valid=False,
            status=VerificationStatus.UNVERIFIED,
            confidence=0.0,
            source_used="Texas Notary Public Commissions (data.texas.gov)",
            details=f"No Texas notaries found for: {query}",
            provenance=ProvenanceMetadata(
                source_url=TEXAS_NOTARY_DATASET_URL,
                source_name="Texas Open Data Portal",
                verification_status=VerificationStatus.UNVERIFIED,
                confidence_score=0.0,
                authoritative_source="data.texas.gov",
            ),
        )
        return {**state, "notary_validation": result}

    # Compute confidence: higher for fewer, tighter matches (e.g. exact name)
    query_lower = query.lower()
    query_words = set(re.findall(r"\w+", query_lower))
    best_match = results[0]
    name_lower = best_match.full_name().lower()
    name_words = set(re.findall(r"\w+", name_lower))
    overlap = len(query_words & name_words) / len(query_words) if query_words else 0
    if len(results) == 1 and overlap >= 0.8:
        confidence = 0.95
    elif len(results) <= 5 and overlap >= 0.5:
        confidence = 0.85
    else:
        confidence = 0.75

    is_valid = confidence >= MIN_CONFIDENCE_THRESHOLD
    summary = ", ".join(r.full_name() for r in results[:5])
    if len(results) > 5:
        summary += f" (+{len(results) - 5} more)"

    result = ValidationResult(
        is_valid=is_valid,
        status=VerificationStatus.VERIFIED if is_valid else VerificationStatus.UNVERIFIED,
        confidence=confidence,
        source_used="Texas Notary Public Commissions (data.texas.gov)",
        details=f"Found {len(results)} notary/notaries: {summary}. "
                f"First match: {best_match.full_name()} (ID {best_match.notary_id}, expires {best_match.expire_date}).",
        provenance=ProvenanceMetadata(
            source_url=TEXAS_NOTARY_DATASET_URL,
            source_name="Texas Open Data Portal",
            verification_status=VerificationStatus.VERIFIED if is_valid else VerificationStatus.UNVERIFIED,
            confidence_score=confidence,
            authoritative_source="data.texas.gov",
        ),
    )

    return {
        **state,
        "notary_validation": result,
    }
