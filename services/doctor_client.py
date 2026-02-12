"""
Doctor API Client

HTTP client for Free Law Project's Doctor microservice.
Doctor provides document conversion: PDF/DOC/DOCX text extraction, OCR, page count,
redaction checks, thumbnails, audio conversion.

Ref: https://github.com/freelawproject/doctor
"""

import requests
from typing import Optional


class DoctorClient:
    """
    Client for the Doctor document conversion API.

    Doctor must be running (e.g. docker run -p 5050:5050 freelawproject/doctor).
    Set DOCTOR_BASE_URL or pass base_url to constructor.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 60):
        self.base_url = (base_url or "").rstrip("/") or "http://localhost:5050"
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if Doctor service is reachable."""
        try:
            r = requests.get(f"{self.base_url}/", timeout=5)
            return r.status_code == 200 and "Heartbeat" in r.text
        except Exception:
            return False

    def extract_doc_text(
        self,
        file_path: str,
        ocr_available: bool = False,
    ) -> dict:
        """
        Extract text from PDF, DOC, DOCX, HTML, TXT, WPD.

        Returns:
            dict with keys: content, err, extension, extracted_by_ocr, page_count
        """
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split("/")[-1], f.read())}
            params = {"ocr_available": ocr_available}
            r = requests.post(
                f"{self.base_url}/extract/doc/text/",
                files=files,
                params=params,
                timeout=self.timeout,
            )
            if r.status_code != 200:
                return {
                    "content": "",
                    "err": r.text or f"HTTP {r.status_code}",
                    "extension": "",
                    "extracted_by_ocr": False,
                    "page_count": None,
                }
            data = r.json()
            return {
                "content": data.get("content", ""),
                "err": data.get("err", ""),
                "extension": data.get("extension", ""),
                "extracted_by_ocr": data.get("extracted_by_ocr", False),
                "page_count": data.get("page_count"),
            }
        except Exception as e:
            return {
                "content": "",
                "err": str(e),
                "extension": "",
                "extracted_by_ocr": False,
                "page_count": None,
            }

    def extract_doc_text_from_bytes(
        self,
        data: bytes,
        filename: str = "document.pdf",
        ocr_available: bool = False,
    ) -> dict:
        """Extract text from document bytes."""
        try:
            files = {"file": (filename, data)}
            params = {"ocr_available": ocr_available}
            r = requests.post(
                f"{self.base_url}/extract/doc/text/",
                files=files,
                params=params,
                timeout=self.timeout,
            )
            if r.status_code != 200:
                return {
                    "content": "",
                    "err": r.text or f"HTTP {r.status_code}",
                    "extension": "",
                    "extracted_by_ocr": False,
                    "page_count": None,
                }
            return r.json()
        except Exception as e:
            return {
                "content": "",
                "err": str(e),
                "extension": "",
                "extracted_by_ocr": False,
                "page_count": None,
            }

    def extract_recap_text(
        self,
        file_path: str,
        strip_margin: bool = False,
    ) -> dict:
        """
        Extract text from RECAP (PACER) PDFs using PDF Plumber + OCR.
        Optimized for federal court filings.
        """
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split("/")[-1], f.read())}
            params = {"strip_margin": strip_margin}
            r = requests.post(
                f"{self.base_url}/extract/recap/text/",
                files=files,
                params=params,
                timeout=self.timeout,
            )
            if r.status_code != 200:
                return {"content": "", "extracted_by_ocr": False, "err": r.text}
            return r.json()
        except Exception as e:
            return {"content": "", "extracted_by_ocr": False, "err": str(e)}

    def get_page_count(self, file_path: str) -> Optional[int]:
        """Get page count for a PDF."""
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split("/")[-1], f.read())}
            r = requests.post(
                f"{self.base_url}/utils/page-count/pdf/",
                files=files,
                timeout=30,
            )
            if r.status_code == 200:
                return int(r.text)
            return None
        except Exception:
            return None

    def get_mime_type(self, file_path: str, mime: bool = True) -> Optional[str]:
        """Get MIME type of a file. mime=True returns application/pdf, False returns descriptive string."""
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split("/")[-1], f.read())}
            r = requests.post(
                f"{self.base_url}/utils/mime-type/",
                files=files,
                params={"mime": mime},
                timeout=30,
            )
            if r.status_code == 200:
                return r.json().get("mimetype")
            return None
        except Exception:
            return None

    def check_redactions(self, file_path: str) -> dict:
        """
        Check PDF for bad redactions (X-Ray).
        Returns dict with error, results (bbox + text per page).
        """
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split("/")[-1], f.read())}
            r = requests.post(
                f"{self.base_url}/utils/check-redactions/pdf/",
                files=files,
                timeout=60,
            )
            if r.status_code == 200:
                return r.json()
            return {"error": True, "msg": r.text}
        except Exception as e:
            return {"error": True, "msg": str(e)}
