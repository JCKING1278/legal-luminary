"""
TDLR (Texas Department of Licensing & Regulation) license lookup.

Fetches licensees from the TDLR All Licenses dataset on data.texas.gov.
Used to surface random Central Texas licensed professionals (with phone numbers)
for the legal-luminary site.

Dataset: https://data.texas.gov/dataset/TDLR-All-Licenses/7358-krk7
"""

from dataclasses import dataclass
from typing import Any, Optional
import random
import re

import requests


TDLR_DATASET_ID = "7358-krk7"
TDLR_BASE_URL = "https://data.texas.gov/resource"

# Central Texas cities/counties for filtering
CENTRAL_TEXAS_CITIES = [
    "Killeen", "Temple", "Belton", "Waco", "Austin", "Georgetown", "Round Rock",
    "Copperas Cove", "Harker Heights", "Cedar Park", "Pflugerville",
    "Salado", "Nolanville", "Gatesville", "Marlin", "McGregor",
]
CENTRAL_TEXAS_COUNTIES = [
    "Bell", "Coryell", "McLennan", "Travis", "Williamson", "Hays", "Burnet", "Lampasas",
]


@dataclass
class TDLRRecord:
    """One TDLR license record with contact info."""
    name: str
    business_name: str
    license_type: str
    license_number: str
    phone: str
    city: str
    county: str
    raw: dict

    @classmethod
    def from_socrata_row(cls, row: dict[str, Any]) -> "TDLRRecord":
        def get(key: str, default: str = "") -> str:
            v = row.get(key) or row.get(key.replace("_", " ").title()) or default
            return str(v).strip() if v is not None else default

        # Column names on data.texas.gov may be title case with spaces
        name = get("name") or get("Name") or (get("first_name", "") + " " + get("last_name", "")).strip()
        business_name = get("business_name") or get("Business Name") or get("businessname", "")
        license_type = get("license_type") or get("License Type") or get("licensetype", "")
        license_number = get("license_number") or get("License Number") or get("licensenumber", "")
        phone = get("business_phone") or get("Business Phone") or get("phone_number") or get("Phone Number") or get("businessphone", "")
        city = get("business_city") or get("Business City") or ""
        if not city:
            # business_city_state_zip or similar
            bcs = get("business_city_state_zip") or get("Business City State Zip") or ""
            city = bcs.split(",")[0].strip() if bcs else ""
        county = get("county") or get("County") or ""

        return cls(
            name=name or "—",
            business_name=business_name,
            license_type=license_type,
            license_number=license_number,
            phone=phone,
            city=city,
            county=county,
            raw=dict(row),
        )

    def display_phone(self) -> str:
        """Return phone formatted for display; empty if missing."""
        p = re.sub(r"\D", "", self.phone)
        if len(p) == 10:
            return f"({p[:3]}) {p[3:6]}-{p[6:]}"
        if len(p) == 11 and p.startswith("1"):
            return f"({p[1:4]}) {p[4:7]}-{p[7:]}"
        return self.phone or ""


def fetch_tdlr_central_texas(
    cities: Optional[list[str]] = None,
    limit: int = 50,
    with_phone_only: bool = True,
    app_token: Optional[str] = None,
) -> list[TDLRRecord]:
    """
    Fetch TDLR licenses for Central Texas cities.

    :param cities: List of city names to filter (default CENTRAL_TEXAS_CITIES).
    :param limit: Max records to request.
    :param with_phone_only: If True, only return records that have a phone number.
    :param app_token: Optional Socrata app token.
    :return: List of TDLRRecord.
    """
    cities = cities or CENTRAL_TEXAS_CITIES
    url = f"{TDLR_BASE_URL}/{TDLR_DATASET_ID}.json"
    params: dict[str, Any] = {"$limit": min(limit, 1000)}
    headers = {"Accept": "application/json"}
    if app_token:
        headers["X-App-Token"] = app_token

    # SoQL $q searches across text fields; use first city then extend
    all_records: list[TDLRRecord] = []
    seen = set()

    for city in cities[:5]:  # limit API calls
        params["$q"] = city
        try:
            r = requests.get(url, params=params, headers=headers, timeout=15)
            r.raise_for_status()
            rows = r.json()
        except requests.RequestException:
            continue
        for row in rows:
            rec = TDLRRecord.from_socrata_row(row)
            if with_phone_only and not rec.phone:
                continue
            key = (rec.name, rec.license_number or rec.phone)
            if key in seen:
                continue
            seen.add(key)
            all_records.append(rec)
            if len(all_records) >= limit:
                break
        if len(all_records) >= limit:
            break

    return all_records


def random_central_texas_professionals(
    notary_limit: int = 3,
    tdlr_limit: int = 3,
    app_token: Optional[str] = None,
) -> dict[str, list[dict]]:
    """
    Fetch random notaries and TDLR licensees in Central Texas for site display.

    Returns a dict suitable for JSON:
      - notaries: list of { name, city, phone, expire_date, ... }
      - tdlr_licensees: list of { name, business_name, license_type, phone, city, ... }
    """
    from services.notary_finder import search_notaries, NotaryRecord

    out: dict[str, list[dict]] = {"notaries": [], "tdlr_licensees": []}

    # Notaries: search by Central Texas cities and pick random
    try:
        from services.notary_finder import NotaryRecord
    except ImportError:
        NotaryRecord = type(None)  # noqa: F811
    for city in random.sample(CENTRAL_TEXAS_CITIES, min(5, len(CENTRAL_TEXAS_CITIES))):
        try:
            results = search_notaries(city=city, limit=20)
        except Exception:
            continue
        for r in results:
            if not isinstance(r, NotaryRecord):
                continue
            name = getattr(r, "full_name", lambda: "")() or (getattr(r, "first_name", "") or "") + " " + (getattr(r, "last_name", "") or "")
            if not name.strip():
                continue
            out["notaries"].append({
                "name": name.strip(),
                "city": (getattr(r, "address", None) or "").split(",")[0].strip() if getattr(r, "address", None) else city,
                "phone": "",
                "expire_date": getattr(r, "expire_date", None) or "",
                "notary_id": getattr(r, "notary_id", None) or "",
            })
        if len(out["notaries"]) >= notary_limit * 5:
            break

    by_name = {n["name"]: n for n in out["notaries"]}
    notaries_list = list(by_name.values())
    out["notaries"] = random.sample(notaries_list, min(notary_limit, len(notaries_list))) if len(notaries_list) >= notary_limit else notaries_list

    # TDLR licensees with phone
    try:
        tdlr_records = fetch_tdlr_central_texas(limit=tdlr_limit * 5, with_phone_only=True, app_token=app_token)
        sampled = random.sample(tdlr_records, min(tdlr_limit, len(tdlr_records))) if len(tdlr_records) >= tdlr_limit else tdlr_records
        for rec in sampled:
            out["tdlr_licensees"].append({
                "name": rec.name,
                "business_name": rec.business_name,
                "license_type": rec.license_type,
                "phone": rec.display_phone() or rec.phone,
                "city": rec.city,
                "county": rec.county,
            })
    except Exception:
        pass

    return out
