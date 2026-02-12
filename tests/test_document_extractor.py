"""
Document extractor tests.

Tests extract_document_text with Doctor (when available) and PyPDF2 fallback.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_extract_document_text_file_not_found():
    """Non-existent file returns err."""
    from services.document_extractor import extract_document_text
    result = extract_document_text("/nonexistent/file.pdf")
    assert result["content"] == ""
    assert result["err"]
    assert result["source"] == "none"


def test_extract_document_text_invalid_input():
    """Invalid input type returns err."""
    from services.document_extractor import extract_document_text
    result = extract_document_text(123)  # type: ignore
    assert result["err"]
    assert result["source"] == "none"


@pytest.mark.skipif(
    not os.path.exists(os.path.join(os.path.dirname(__file__), "..", "..", "doctor", "doctor", "test_assets", "vector-pdf.pdf")),
    reason="Doctor test assets not present",
)
def test_extract_document_text_pypdf2_fallback():
    """When Doctor unavailable, PyPDF2 fallback extracts from PDF."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        pytest.skip("PyPDF2 not installed")

    asset_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "doctor", "doctor", "test_assets", "vector-pdf.pdf"
    )
    from services.document_extractor import extract_document_text

    with patch("services.document_extractor._get_doctor_client") as mock_get:
        mock_client = MagicMock()
        mock_client.is_available.return_value = False
        mock_get.return_value = mock_client

        result = extract_document_text(asset_path, use_doctor=True)
        # Should fall back to PyPDF2
        assert result["content"]
        assert result["source"] in ("pypdf2", "pdfplumber", "doctor")
        assert result["page_count"] == 30


@patch("services.document_extractor._get_doctor_client")
def test_extract_document_text_uses_doctor_when_available(mock_get):
    """When Doctor available, uses Doctor for extraction."""
    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    mock_client.extract_doc_text_from_bytes.return_value = {
        "content": "Extracted by Doctor",
        "err": "",
        "extension": "pdf",
        "extracted_by_ocr": False,
        "page_count": 5,
    }
    mock_get.return_value = mock_client

    # Create minimal PDF bytes
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes)
        f.flush()
        path = f.name

    try:
        from services.document_extractor import extract_document_text
        result = extract_document_text(path, use_doctor=True)
        assert result["content"] == "Extracted by Doctor"
        assert result["source"] == "doctor"
        assert result["page_count"] == 5
    finally:
        os.unlink(path)


def test_extract_document_text_from_bytes_pypdf2():
    """Extract from bytes using PyPDF2 when Doctor unavailable."""
    try:
        from PyPDF2 import PdfWriter, PdfReader
        import io
    except ImportError:
        pytest.skip("PyPDF2 not installed")

    # Create minimal valid PDF
    buf = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    writer.write(buf)
    pdf_bytes = buf.getvalue()

    from services.document_extractor import extract_document_text

    with patch("services.document_extractor._get_doctor_client") as mock_get:
        mock_client = MagicMock()
        mock_client.is_available.return_value = False
        mock_get.return_value = mock_client

        result = extract_document_text(pdf_bytes, use_doctor=True)
        assert result["source"] in ("pypdf2", "pdfplumber")
        assert result["page_count"] == 1
