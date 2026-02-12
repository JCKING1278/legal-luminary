"""
Legal Luminary Services

Document processing and external API clients.
- doctor_client: Free Law Project Doctor API client (PDF/DOC/DOCX text extraction)
- document_extractor: Unified document text extraction (Doctor + fallbacks)
"""

from .doctor_client import DoctorClient
from .document_extractor import extract_document_text

__all__ = ["DoctorClient", "extract_document_text"]
