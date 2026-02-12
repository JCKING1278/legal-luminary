#!/usr/bin/env python3
"""
Test document extraction on the Texas Work Group on Blockchain Matters PDF.
Run from legal-luminary directory: python3 test_pdf_extraction.py
"""
import sys
from pathlib import Path

# Ensure legal-luminary is on path
root = Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from services.document_extractor import extract_document_text


def main():
    pdf_path = "/tmp/texas_blockchain_report.pdf"
    if not Path(pdf_path).exists():
        print(f"PDF not found: {pdf_path}")
        print("Download with: curl -L -o /tmp/texas_blockchain_report.pdf '<URL>'")
        return 1

    print("Extracting text from Texas Work Group on Blockchain Matters report...")
    result = extract_document_text(
        pdf_path,
        ocr_available=True,
        use_doctor=True,
        is_recap=False,
    )

    print(f"\n--- Result ---")
    print(f"Source: {result['source']}")
    print(f"Page count: {result.get('page_count', 'N/A')}")
    print(f"OCR used: {result.get('extracted_by_ocr', False)}")
    if result.get("err"):
        print(f"Error: {result['err']}")

    content = result.get("content", "")
    print(f"\n--- Extracted text (first 2000 chars) ---\n")
    print(content[:2000] if content else "(no text extracted)")
    if len(content) > 2000:
        print(f"\n... [truncated; total {len(content)} chars]")

    return 0 if content else 1


if __name__ == "__main__":
    sys.exit(main())
