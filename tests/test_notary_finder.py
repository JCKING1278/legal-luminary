"""
Texas Notary Public finder tests.

Unit tests use mocks. Integration tests hit the live Texas Open Data API.
"""

import os
import sys

import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.notary_finder import NotaryFinder, NotaryRecord, search_notaries


def test_notary_record_from_socrata_row():
    row = {
        "notary_id": "134751650",
        "first_name": "Kathy",
        "last_name": "Lapham",
        "effective_date": "02/07/2024",
        "expire_date": "02/07/2028",
        "address": "8701 New Trails Dr\nThe Woodlands, TX 77381",
        "email_address": "kathy@example.org",
        "surety_company": "Western Surety",
        "agency": "American Association of Notaries Inc",
    }
    rec = NotaryRecord.from_socrata_row(row)
    assert rec.notary_id == "134751650"
    assert rec.full_name() == "Kathy Lapham"
    assert rec.expire_date == "02/07/2028"


def test_notary_record_handles_missing_fields():
    rec = NotaryRecord.from_socrata_row({})
    assert rec.notary_id == ""
    assert rec.full_name() == ""


@patch("requests.get")
def test_notary_finder_search(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: [
            {
                "notary_id": "133853828",
                "first_name": "Monika",
                "last_name": "Sharma",
                "effective_date": "07/12/2022",
                "expire_date": "07/12/2026",
                "address": "plano, TX 75025",
                "email_address": "test@example.com",
                "surety_company": "Travelers",
                "agency": "Huckleberry",
            }
        ],
    )
    finder = NotaryFinder(
        base_url="https://data.texas.gov/resource",
        dataset_id="gmd3-bnrd",
    )
    results = finder.search(query="plano", limit=5)
    assert len(results) == 1
    assert results[0].last_name == "Sharma"
    assert "plano" in results[0].address.lower()
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "gmd3-bnrd.json" in call_args[0][0]
    assert call_args[1]["params"]["$q"] == "plano"
    assert call_args[1]["params"]["$limit"] == 5


@patch("requests.get")
def test_notary_finder_get_by_id(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: [
            {
                "notary_id": "134751650",
                "first_name": "Kathy",
                "last_name": "Lapham",
                "effective_date": "02/07/2024",
                "expire_date": "02/07/2028",
                "address": "The Woodlands, TX",
                "email_address": "k@y.org",
                "surety_company": "Western",
                "agency": "AAN",
            }
        ],
    )
    finder = NotaryFinder(base_url="https://data.texas.gov/resource", dataset_id="gmd3-bnrd")
    rec = finder.get_by_id("134751650")
    assert rec is not None
    assert rec.notary_id == "134751650"
    assert rec.full_name() == "Kathy Lapham"


@patch("requests.get")
def test_notary_finder_get_by_id_not_found(mock_get):
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [])
    finder = NotaryFinder(base_url="https://data.texas.gov/resource", dataset_id="gmd3-bnrd")
    assert finder.get_by_id("999999999") is None


@pytest.mark.integration
def test_notary_finder_live_search():
    """Hit Texas Open Data API; skip if offline or API changes."""
    finder = NotaryFinder()
    results = finder.search(query="Austin", limit=3)
    assert isinstance(results, list)
    # API may return 0 or more
    for r in results:
        assert isinstance(r, NotaryRecord)
        assert r.notary_id
        assert r.full_name()
