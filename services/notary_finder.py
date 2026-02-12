"""
Texas Notary Public finder.

Searches the Texas Notary Public Commissions dataset on the Texas Open Data
Portal (Socrata). Data is from the Office of the Texas Secretary of State.

Dataset: https://data.texas.gov/dataset/Texas-Notary-Public-Commissions/gmd3-bnrd
"""

from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass
class NotaryRecord:
    """One notary public record from the Texas SOS dataset."""

    notary_id: str
    first_name: str
    last_name: str
    effective_date: str
    expire_date: str
    address: str
    email_address: str
    surety_company: str
    agency: str

    @classmethod
    def from_socrata_row(cls, row: dict[str, Any]) -> "NotaryRecord":
        return cls(
            notary_id=str(row.get("notary_id") or ""),
            first_name=str(row.get("first_name") or ""),
            last_name=str(row.get("last_name") or ""),
            effective_date=str(row.get("effective_date") or ""),
            expire_date=str(row.get("expire_date") or ""),
            address=str(row.get("address") or ""),
            email_address=str(row.get("email_address") or ""),
            surety_company=str(row.get("surety_company") or ""),
            agency=str(row.get("agency") or ""),
        )

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class NotaryFinder:
    """
    Client for searching Texas Notary Public Commissions via the Socrata SODA API.
    """

    def __init__(
        self,
        base_url: str = "https://data.texas.gov/resource",
        dataset_id: str = "gmd3-bnrd",
        app_token: Optional[str] = None,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.dataset_id = dataset_id
        self.app_token = app_token
        self.timeout = timeout
        self._resource_url = f"{self.base_url}/{self.dataset_id}.json"

    def _headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self.app_token:
            headers["X-App-Token"] = self.app_token
        return headers

    def search(
        self,
        query: Optional[str] = None,
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[NotaryRecord]:
        """
        Search notaries by free text and/or by first name, last name, or city.

        :param query: Full-text search (Socrata $q) across name, address, etc.
        :param first_name: Filter by first name (case-insensitive contains).
        :param last_name: Filter by last name (case-insensitive contains).
        :param city: Filter by city (searches inside address).
        :param limit: Max results (default 50, API may cap).
        :param offset: Pagination offset.
        :return: List of NotaryRecord.
        """
        params: dict[str, str | int] = {
            "$limit": min(limit, 1000),
            "$offset": offset,
        }
        if query and query.strip():
            params["$q"] = query.strip()
        where_parts = []
        if first_name and first_name.strip():
            term = first_name.strip().replace("'", "''")
            where_parts.append(f"lower(first_name) like '%{term.lower()}%'")
        if last_name and last_name.strip():
            term = last_name.strip().replace("'", "''")
            where_parts.append(f"lower(last_name) like '%{term.lower()}%'")
        if city and city.strip():
            term = city.strip().replace("'", "''")
            where_parts.append(f"lower(address) like '%{term.lower()}%'")
        if where_parts:
            params["$where"] = " and ".join(where_parts)

        try:
            r = requests.get(
                self._resource_url,
                params=params,
                headers=self._headers(),
                timeout=self.timeout,
            )
            r.raise_for_status()
            rows = r.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Notary API request failed: {e}") from e

        return [NotaryRecord.from_socrata_row(row) for row in rows]

    def get_by_id(self, notary_id: str) -> Optional[NotaryRecord]:
        """Fetch a single notary by commission ID."""
        params = {"notary_id": notary_id, "$limit": 1}
        try:
            r = requests.get(
                self._resource_url,
                params=params,
                headers=self._headers(),
                timeout=self.timeout,
            )
            r.raise_for_status()
            rows = r.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Notary API request failed: {e}") from e
        if not rows:
            return None
        return NotaryRecord.from_socrata_row(rows[0])


def search_notaries(
    query: Optional[str] = None,
    *,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 50,
) -> list[NotaryRecord]:
    """
    Convenience function to search notaries using app config.

    Uses TEXAS_SODA_BASE, TEXAS_NOTARY_DATASET_ID, and SOCRATA_APP_TOKEN
    from config.settings when available.
    """
    try:
        from config.settings import (
            SOCRATA_APP_TOKEN,
            TEXAS_NOTARY_DATASET_ID,
            TEXAS_SODA_BASE,
        )
        base = TEXAS_SODA_BASE
        dataset_id = TEXAS_NOTARY_DATASET_ID
        app_token = SOCRATA_APP_TOKEN or None
    except ImportError:
        base = "https://data.texas.gov/resource"
        dataset_id = "gmd3-bnrd"
        app_token = None
    finder = NotaryFinder(base_url=base, dataset_id=dataset_id, app_token=app_token)
    return finder.search(
        query=query,
        first_name=first_name,
        last_name=last_name,
        city=city,
        limit=limit,
    )
