"""
Research Input Validator

Ensures that the required research artifacts are present before the generation pipeline starts.
"""
import os
from typing import Dict
from state import ValidationResult, ProvenanceMetadata, VerificationStatus

REQUIRED_FILES = [
    "research_paper.pdf",
    "PRD.md",
]
BASE_PATH = "/Users/sweeden/research_paper"

def validate_research_input(state: Dict) -> Dict:
    """Validate presence of required research artifacts.

    Adds a `research_validation` field to the PipelineState with provenance.
    """
    missing = []
    for fn in REQUIRED_FILES:
        path = os.path.join(BASE_PATH, fn)
        if not os.path.isfile(path):
            missing.append(fn)
    is_valid = len(missing) == 0
    status = VerificationStatus.VERIFIED if is_valid else VerificationStatus.UNVERIFIED
    provenance: ProvenanceMetadata = {
        "source_url": BASE_PATH,
        "source_name": "research artifacts",
        "retrieval_date": os.path.getmtime(BASE_PATH) if os.path.isdir(BASE_PATH) else "",  # not used
        "verification_status": status,
        "confidence_score": 1.0 if is_valid else 0.0,
        "authoritative_source": "research_validation",
    }
    details = f"Missing files: {', '.join(missing)}" if missing else "All required research artifacts present."
    result: ValidationResult = {
        "is_valid": is_valid,
        "status": status,
        "confidence": 1.0 if is_valid else 0.0,
        "source_used": "research_validator",
        "details": details,
        "provenance": provenance,
    }
    return {"research_validation": result}
