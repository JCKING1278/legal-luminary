"""Node 2: URL syntax validation and HTTP reachability checking.

Performs RFC 3986 syntax validation, allowlist checking, HTTP reachability,
equivalence partitioning (Valid/Redirect/Invalid), and boundary analysis
(redirect chain depth, URL length).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from ..config import REPO_ROOT
from ..state import VerificationState
from ..url_utils import (
    host_is_allowed,
    normalize_host,
    validate_url_syntax,
    MAX_REDIRECT_HOPS,
)


def _http_check_urls(
    urls: List[str],
    *,
    skip_urls: set,
    skip_hosts: set,
) -> Dict[str, Dict[str, Any]]:
    """Check URL reachability. Returns per-url result dict."""
    results: Dict[str, Dict[str, Any]] = {}
    unique = sorted(set(urls))
    timeout = httpx.Timeout(connect=10.0, read=20.0, write=10.0, pool=10.0)
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
    headers = {
        "User-Agent": "legal-luminary-verifier/0.2 (+https://www.legalluminary.com)"
    }

    with httpx.Client(
        follow_redirects=True, timeout=timeout, limits=limits, headers=headers
    ) as client:
        for url in unique:
            host = normalize_host(url)
            host_is_skipped = False
            if host:
                host_is_skipped = host in skip_hosts or any(
                    host.endswith("." + h) for h in skip_hosts
                )
            if url in skip_urls or host_is_skipped:
                results[url] = {
                    "skipped": True,
                    "ok": True,
                    "status": None,
                    "final_url": None,
                    "error": None,
                    "redirect_count": 0,
                    "ep_class": "skipped",
                }
                continue

            ok = False
            status: Optional[int] = None
            final_url: Optional[str] = None
            err: Optional[str] = None
            redirect_count = 0

            try:
                r = client.head(url)
                status = r.status_code
                final_url = str(r.url)
                redirect_count = len(r.history)
                if status == 405:
                    r = client.get(url)
                    status = r.status_code
                    final_url = str(r.url)
                    redirect_count = len(r.history)
                ok = status < 400
            except Exception as e:
                err = f"{type(e).__name__}: {e}"

            # Equivalence partitioning class
            if err:
                ep_class = "error"
            elif status is not None and status >= 400:
                ep_class = "invalid"
            elif redirect_count > 0:
                ep_class = "redirect"
            else:
                ep_class = "valid"

            results[url] = {
                "skipped": False,
                "ok": bool(ok),
                "status": status,
                "final_url": final_url,
                "error": err,
                "redirect_count": redirect_count,
                "ep_class": ep_class,
            }
    return results


def validate_urls_node(state: VerificationState) -> dict:
    """Node 2: validate URL syntax, check allowlist, perform HTTP reachability."""
    all_urls = state["all_urls"]
    allowlist_rules = state["allowlist_rules"]
    file_results = state["file_results"]
    exceptions = state["exceptions"]

    skip_reachability_urls = {str(u) for u in exceptions["skip_reachability_urls"]}
    skip_reachability_hosts = {
        str(h).lower() for h in exceptions["skip_reachability_hosts"]
    }

    # 1. RFC 3986 syntax validation
    url_syntax_results: Dict[str, dict] = {}
    for url in all_urls:
        url_syntax_results[url] = validate_url_syntax(url)

    # 2. Allowlist checking (per-file)
    allowlist_violations: List[dict] = []
    errors: List[str] = []
    for rel, info in file_results.items():
        not_allowed: List[str] = []
        for u in info["urls"]:
            host = normalize_host(u)
            if host is None:
                continue
            if not host_is_allowed(host, allowlist_rules):
                not_allowed.append(u)
        if not_allowed:
            err_msg = f"{rel}: non-allowlisted URL(s): {not_allowed}"
            info["errors"].append(err_msg)
            info["ok"] = False
            errors.append(err_msg)
            for u in not_allowed:
                allowlist_violations.append(
                    {"file": rel, "url": u, "host": normalize_host(u)}
                )

    # 3. HTTP reachability
    reachability_results = _http_check_urls(
        all_urls,
        skip_urls=skip_reachability_urls,
        skip_hosts=skip_reachability_hosts,
    )

    # 4. Boundary analysis: flag excessive redirect chains
    for url, result in reachability_results.items():
        if result.get("redirect_count", 0) > MAX_REDIRECT_HOPS:
            result["boundary_warning"] = (
                f"redirect chain depth {result['redirect_count']} exceeds limit of {MAX_REDIRECT_HOPS}"
            )

    # 5. Attach reachability failures to per-file results
    for rel, info in file_results.items():
        bad = []
        for u in info["urls"]:
            host = normalize_host(u)
            if host is None:
                continue
            r = reachability_results.get(u)
            if r and not r.get("ok", False):
                bad.append({"url": u, **r})
        if bad:
            err_msg = f"{rel}: unreachable URL(s): {bad}"
            info["errors"].append(err_msg)
            info["ok"] = False

    return {
        "url_syntax_results": url_syntax_results,
        "reachability_results": reachability_results,
        "allowlist_violations": allowlist_violations,
        "file_results": file_results,
        "errors": errors,
    }
