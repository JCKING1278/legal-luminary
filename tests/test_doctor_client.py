"""
Doctor API client tests.

Uses mocks when Doctor is not available.
Integration tests require: docker run -p 5050:5050 freelawproject/doctor
"""

import pytest
from unittest.mock import patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.doctor_client import DoctorClient


def test_doctor_client_is_available_false_when_unreachable():
    """Doctor not running -> is_available returns False."""
    client = DoctorClient(base_url="http://localhost:59999")
    assert client.is_available() is False


@patch("requests.get")
def test_doctor_client_is_available_true(mock_get):
    """Doctor running -> is_available returns True."""
    mock_get.return_value = MagicMock(status_code=200, text="Heartbeat detected.")
    client = DoctorClient(base_url="http://localhost:5050")
    assert client.is_available() is True


@patch("requests.post")
def test_extract_doc_text_success(mock_post):
    """Extract doc text returns content from Doctor."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "content": "(Slip Opinion) OCTOBER TERM, 2012 1",
            "err": "",
            "extension": "pdf",
            "extracted_by_ocr": False,
            "page_count": 30,
        },
    )
    client = DoctorClient(base_url="http://localhost:5050")

    # Use bytes since we may not have test file
    result = client.extract_doc_text_from_bytes(
        b"%PDF-1.4 fake pdf content", filename="test.pdf"
    )
    assert result["content"] == "(Slip Opinion) OCTOBER TERM, 2012 1"
    assert result["extracted_by_ocr"] is False
    assert result["page_count"] == 30


@patch("requests.post")
def test_extract_doc_text_http_error(mock_post):
    """Extract doc text handles HTTP error."""
    mock_post.return_value = MagicMock(status_code=500, text="Server error")
    client = DoctorClient(base_url="http://localhost:5050")
    result = client.extract_doc_text_from_bytes(b"fake", filename="x.pdf")
    assert result["content"] == ""
    assert "500" in result["err"] or "Server" in result["err"]


def test_extract_doc_text_file_not_found():
    """Extract from missing file returns err."""
    client = DoctorClient(base_url="http://localhost:5050")
    result = client.extract_doc_text("/nonexistent/path/file.pdf")
    assert result["content"] == ""
    assert result["err"]


@pytest.mark.skipif(
    not os.path.exists(
        os.path.join(os.path.dirname(__file__), "..", "..", "doctor", "doctor", "test_assets", "vector-pdf.pdf")
    ),
    reason="Doctor test assets not present (run: git submodule update --init doctor)",
)
def test_extract_doc_text_integration():
    """Integration: extract from Doctor vector-pdf.pdf when Doctor + assets available."""
    asset_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "doctor", "doctor", "test_assets", "vector-pdf.pdf"
    )
    if not os.path.exists(asset_path):
        pytest.skip("Doctor test_assets/vector-pdf.pdf not found")

    client = DoctorClient(base_url="http://localhost:5050")
    if not client.is_available():
        pytest.skip("Doctor not running at localhost:5050")

    result = client.extract_doc_text(asset_path, ocr_available=False)
    assert result["content"]
    assert "OCTOBER" in result["content"] or "Slip" in result["content"]
    assert result["page_count"] == 30
