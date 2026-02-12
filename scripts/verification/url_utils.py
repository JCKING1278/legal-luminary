"""URL extraction, normalization, validation, and allowlist checking."""

from __future__ import annotations

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from .config import AllowHostRule


URL_RE = re.compile(r"https?://[^\s<>()\[\]\"']+")

EXAMPLE_URL_SUBSTRINGS = (
    "yourusername.github.io/",
    "sweeden-ttu.github.io/myblog",
    "sweeden-ttu.github.io",
    "github.io/project",
)

# RFC 3986: valid percent-encoded sequences
_PERCENT_RE = re.compile(r"%[0-9A-Fa-f]{2}")
_BAD_PERCENT_RE = re.compile(r"%(?![0-9A-Fa-f]{2})")

# Maximum URL length (IE/Edge legacy limit, widely used as practical ceiling)
MAX_URL_LENGTH = 2083

# Maximum redirect hops before we consider it excessive
MAX_REDIRECT_HOPS = 5


def extract_urls_from_text(text: str) -> List[str]:
    """Extract all http(s) URLs from text, cleaning trailing punctuation."""
    urls = URL_RE.findall(text)
    cleaned: List[str] = []
    for u in urls:
        u2 = u.rstrip("`'\".,);:!?]")
        cleaned.append(u2)
    return cleaned


def normalize_host(url: str) -> Optional[str]:
    """Extract and normalize the hostname from a URL. Returns None for invalid/local URLs."""
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None
    host = parsed.hostname
    if not host:
        return None
    host = host.lower()
    if host in {"localhost", "127.0.0.1"}:
        return None
    return host


def host_is_allowed(host: str, rules: List[AllowHostRule]) -> bool:
    """Check if a host matches any allowlist rule."""
    host = host.lower().strip(".")
    for rule in rules:
        if host == rule.host:
            return True
        if rule.allow_subdomains and host.endswith("." + rule.host):
            return True
    return False


def get_host_category(host: str, rules: List[AllowHostRule]) -> Optional[str]:
    """Return the allowlist category for a host, or None if not on allowlist."""
    host = host.lower().strip(".")
    for rule in rules:
        if host == rule.host:
            return rule.category
        if rule.allow_subdomains and host.endswith("." + rule.host):
            return rule.category
    return None


def is_example_url(url: str) -> bool:
    """Check if a URL is a tutorial/example URL that should skip reachability."""
    u = url.lower()
    return any(s in u for s in EXAMPLE_URL_SUBSTRINGS)


def validate_url_syntax(url: str) -> Dict[str, object]:
    """
    Validate URL syntax per RFC 3986.

    Returns dict with:
        url: the original URL
        valid: bool
        issues: list of issue descriptions
    """
    issues: List[str] = []

    # Length check
    if len(url) > MAX_URL_LENGTH:
        issues.append(f"exceeds {MAX_URL_LENGTH} char limit ({len(url)} chars)")

    # Parse
    try:
        parsed = urlparse(url)
    except Exception as e:
        return {"url": url, "valid": False, "issues": [f"unparseable: {e}"]}

    # Scheme validation
    if parsed.scheme not in {"http", "https"}:
        issues.append(f"invalid scheme: {parsed.scheme!r}")

    # Authority (netloc) must be present
    if not parsed.netloc:
        issues.append("missing authority (netloc)")

    # Hostname validation
    if parsed.hostname:
        host = parsed.hostname
        # Check for valid hostname characters
        if not re.match(r"^[a-zA-Z0-9._-]+$", host):
            issues.append(f"invalid hostname characters: {host!r}")
    else:
        issues.append("missing hostname")

    # Percent-encoding validation on path + query + fragment
    for part_name, part_value in [
        ("path", parsed.path),
        ("query", parsed.query),
        ("fragment", parsed.fragment),
    ]:
        if part_value and _BAD_PERCENT_RE.search(part_value):
            issues.append(f"malformed percent-encoding in {part_name}")

    return {"url": url, "valid": len(issues) == 0, "issues": issues}
