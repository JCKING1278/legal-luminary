"""
Document text extractor.

Unified interface for extracting text from PDF, DOC, DOCX, etc.
Uses Doctor API when available, falls back to PyPDF2/pdfplumber for PDFs.
"""

import os
from pathlib import Path
from typing import Optional

# Lazy imports for optional deps
_doctor_client = None
_pypdf2_available = None
_pdfplumber_available = None


def _get_doctor_client():
    global _doctor_client
    if _doctor_client is None:
        from .doctor_client import DoctorClient
        try:
            from config.settings import DOCTOR_BASE_URL
            base = DOCTOR_BASE_URL or "http://localhost:5050"
        except ImportError:
            base = "http://localhost:5050"
        _doctor_client = DoctorClient(base_url=base)
    return _doctor_client


def _check_pypdf2():
    global _pypdf2_available
    if _pypdf2_available is None:
        try:
            from PyPDF2 import PdfReader
            _pypdf2_available = True
        except ImportError:
            _pypdf2_available = False
    return _pypdf2_available


def _check_pdfplumber():
    global _pdfplumber_available
    if _pdfplumber_available is None:
        try:
            import pdfplumber
            _pdfplumber_available = True
        except ImportError:
            _pdfplumber_available = False
    return _pdfplumber_available


def extract_document_text(
    path_or_bytes,
    *,
    ocr_available: bool = False,
    use_doctor: bool = True,
    is_recap: bool = False,
) -> dict:
    """
    Extract text from a document (PDF, DOC, DOCX, etc.).

    :param path_or_bytes: File path (str) or file bytes (bytes)
    :param ocr_available: Whether to use OCR for scanned PDFs (Doctor only)
    :param use_doctor: Try Doctor API first if available
    :param is_recap: Use RECAP extraction for PACER PDFs
    :return: dict with content, extracted_by_ocr, page_count, source
    """
    result = {
        "content": "",
        "extracted_by_ocr": False,
        "page_count": None,
        "source": "none",
        "err": "",
    }

    # Normalize input
    filepath = None
    file_bytes = None
    filename = "document.pdf"

    if isinstance(path_or_bytes, (str, Path)):
        p = Path(path_or_bytes)
        if not p.exists():
            result["err"] = f"File not found: {path_or_bytes}"
            return result
        filepath = str(p)
        filename = p.name
        with open(filepath, "rb") as f:
            file_bytes = f.read()
    elif isinstance(path_or_bytes, bytes):
        file_bytes = path_or_bytes
        filename = "document.pdf"
    else:
        result["err"] = "path_or_bytes must be str, Path, or bytes"
        return result

    # 1. Try Doctor API
    if use_doctor:
        client = _get_doctor_client()
        if client.is_available():
            try:
                if is_recap and filepath:
                    doc_result = client.extract_recap_text(
                        filepath, strip_margin=True
                    )
                    result["content"] = doc_result.get("content", "")
                    result["extracted_by_ocr"] = doc_result.get(
                        "extracted_by_ocr", False
                    )
                elif filepath:
                    doc_result = client.extract_doc_text(
                        filepath, ocr_available=ocr_available
                    )
                    result["content"] = doc_result.get("content", "")
                    result["err"] = doc_result.get("err", "")
                    result["extracted_by_ocr"] = doc_result.get(
                        "extracted_by_ocr", False
                    )
                    result["page_count"] = doc_result.get("page_count")
                else:
                    doc_result = client.extract_doc_text_from_bytes(
                        file_bytes, filename=filename, ocr_available=ocr_available
                    )
                    result["content"] = doc_result.get("content", "")
                    result["err"] = doc_result.get("err", "")
                    result["extracted_by_ocr"] = doc_result.get(
                        "extracted_by_ocr", False
                    )
                    result["page_count"] = doc_result.get("page_count")

                if result["content"]:
                    result["source"] = "doctor"
                    return result
            except Exception as e:
                result["err"] = str(e)

    # 2. Fallback: PDF-only with PyPDF2 or pdfplumber
    ext = (filename or "").lower().split(".")[-1]
    if ext not in ("pdf",):
        result["err"] = result["err"] or "No Doctor and non-PDF; install Doctor for DOC/DOCX"
        return result

    if _check_pypdf2():
        try:
            from PyPDF2 import PdfReader
            import io
            reader = PdfReader(io.BytesIO(file_bytes) if file_bytes else filepath)
            result["page_count"] = len(reader.pages)
            parts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
            result["content"] = "\n\n".join(parts)
            if result["content"]:
                result["source"] = "pypdf2"
                return result
        except Exception as e:
            result["err"] = str(e)

    if _check_pdfplumber():
        try:
            import pdfplumber
            import io
            with pdfplumber.open(io.BytesIO(file_bytes) if file_bytes else filepath) as pdf:
                result["page_count"] = len(pdf.pages)
                parts = []
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        parts.append(t)
                result["content"] = "\n\n".join(parts)
                if result["content"]:
                    result["source"] = "pdfplumber"
                    return result
        except Exception as e:
            result["err"] = result["err"] or str(e)

    result["err"] = result["err"] or "Could not extract text"
    return result
