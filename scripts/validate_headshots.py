#!/usr/bin/env python3
"""
Script to validate candidate headshot URLs.

The script reads the audit file produced by LL-001:
```
_data/audit_headshots.json
```
Each entry contains:
- `slug` : candidate slug
- `headshot_url` : URL or path

For each candidate we attempt to fetch the image using a simple HEAD request.
If the response is 200 and content-type starts with `image/`, we mark the
candidate as having a verified headshot.  The result is written back to the
same JSON file under a new key ``headshot_verified``.
"""
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

AUDIT_PATH = "_data/audit_headshots.json"


def check_image(url: str) -> bool:
    try:
        req = Request(url, method="HEAD")
        with urlopen(req, timeout=10) as resp:
            if resp.status == 200 and resp.getheader("Content-Type", "").startswith("image/"):
                return True
    except (URLError, HTTPError):
        pass
    return False


def main() -> int:
    if not os.path.exists(AUDIT_PATH):
        print(f"Audit file {AUDIT_PATH} not found", file=sys.stderr)
        return 1
    with open(AUDIT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    updated = False
    for entry in data.get("candidates", []):
        url = entry.get("headshot_url")
        if not url:
            continue
        verified = check_image(url)
        if verified != entry.get("headshot_verified"):
            entry["headshot_verified"] = verified
            updated = True
    if updated:
        with open(AUDIT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    print(f"Processed {len(data.get('candidates', []))} candidates. Updated: {updated}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
