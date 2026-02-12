"""LangGraph state schema for the verification pipeline."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from .config import AllowHostRule


class FileResult(TypedDict):
    sha256: str
    front_matter: Dict[str, Any]
    urls: List[str]
    errors: List[str]
    ok: bool


class URLCheckResult(TypedDict):
    skipped: bool
    ok: bool
    status: Optional[int]
    final_url: Optional[str]
    error: Optional[str]


class URLClassification(TypedDict):
    url: str
    host: str
    category: str  # "government", "news", "vendor", "unknown"
    llm_classified: bool  # True if LLM made the call, False if from allowlist
    confidence: float  # 0.0-1.0, 1.0 for allowlist matches


class URLSyntaxResult(TypedDict):
    url: str
    valid: bool
    issues: List[str]


class VerificationState(TypedDict):
    # Input config
    allowlist_rules: List[AllowHostRule]
    exceptions: dict
    markdown_files: List[str]

    # Node 1: extract_content output
    file_results: Dict[str, FileResult]
    all_urls: List[str]

    # Node 2: url_validation output
    url_syntax_results: Dict[str, URLSyntaxResult]
    reachability_results: Dict[str, URLCheckResult]
    allowlist_violations: Annotated[List[dict], operator.add]

    # Node 3: classify_sources output
    classifications: Dict[str, URLClassification]
    openai_available: bool
    classification_warnings: Annotated[List[str], operator.add]

    # Node 4: validation_action output
    coverage_metrics: dict

    # Final output
    manifest: Dict[str, Any]
    exit_code: int
    errors: Annotated[List[str], operator.add]
