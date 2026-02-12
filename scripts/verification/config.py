"""Path constants and configuration loading for the verification pipeline."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = REPO_ROOT / "verification" / "allowlist.yml"
EXCEPTIONS_PATH = REPO_ROOT / "verification" / "exceptions.yml"
MANIFEST_PATH = REPO_ROOT / "verification" / "manifest.json"
CACHE_PATH = REPO_ROOT / "verification" / "classification_cache.json"

IN_SCOPE_DIRS = [
    REPO_ROOT / "_pages",
    REPO_ROOT / "_posts",
]

EXCLUDE_DIR_NAMES = {
    ".git",
    ".github",
    "_site",
    "node_modules",
    "vendor",
}


class VerificationError(Exception):
    pass


@dataclass(frozen=True)
class AllowHostRule:
    host: str
    allow_subdomains: bool
    category: str = "unspecified"


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        raise VerificationError(f"Missing required config file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise VerificationError(f"Config file must be a mapping: {path}")
    return data


def load_allowlist() -> List[AllowHostRule]:
    raw = _load_yaml(ALLOWLIST_PATH)
    hosts = raw.get("hosts", [])
    if not isinstance(hosts, list):
        raise VerificationError(f"{ALLOWLIST_PATH}: 'hosts' must be a list")
    rules: List[AllowHostRule] = []
    for item in hosts:
        if not isinstance(item, dict):
            raise VerificationError(f"{ALLOWLIST_PATH}: each host entry must be a mapping")
        host = item.get("host")
        allow_subdomains = item.get("allow_subdomains", False)
        category = item.get("category", "unspecified")
        if not isinstance(host, str) or not host.strip():
            raise VerificationError(f"{ALLOWLIST_PATH}: host entry missing 'host'")
        if not isinstance(allow_subdomains, bool):
            raise VerificationError(
                f"{ALLOWLIST_PATH}: allow_subdomains must be boolean for host={host}"
            )
        if not isinstance(category, str):
            category = "unspecified"
        rules.append(
            AllowHostRule(
                host=host.lower(),
                allow_subdomains=allow_subdomains,
                category=category,
            )
        )
    return rules


def load_exceptions() -> dict:
    raw = _load_yaml(EXCEPTIONS_PATH)
    for key in [
        "skip_reachability_urls",
        "skip_reachability_hosts",
        "extra_allowlist_hosts",
        "exempt_traceability_files",
    ]:
        val = raw.get(key, [])
        if val is None:
            raw[key] = []
        elif not isinstance(val, list):
            raise VerificationError(f"{EXCEPTIONS_PATH}: '{key}' must be a list")
    return raw


def load_config() -> Dict[str, Any]:
    """Load all configuration and return a dict suitable for initial pipeline state."""
    allow_rules = load_allowlist()
    exceptions = load_exceptions()

    extra_allow_hosts = {str(h).lower() for h in exceptions["extra_allowlist_hosts"]}
    allow_rules = allow_rules + [
        AllowHostRule(host=h, allow_subdomains=True, category="exception")
        for h in extra_allow_hosts
    ]

    return {
        "allowlist_rules": allow_rules,
        "exceptions": exceptions,
    }
