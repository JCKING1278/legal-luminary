#!/usr/bin/env python3
"""
Run Legal Luminary tests including Doctor integration and ported Doctor unit tests.

Legal Luminary tests:
  pytest tests/test_text_extraction.py tests/test_doctor_client.py tests/test_document_extractor.py -v

For Doctor integration tests (require Doctor running):
  docker run -d -p 5050:5050 freelawproject/doctor:latest
  pytest tests/test_doctor_client.py tests/test_document_extractor.py -v -k integration

To run upstream Doctor tests (requires doctor submodule + docker):
  cd doctor && docker compose up -d
  docker exec -it doctor python3 -m unittest discover doctor
  # Or see doctor/DEVELOPING.md
"""

import os
import subprocess
import sys


def main():
    cwd = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cwd)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_text_extraction.py",
            "tests/test_doctor_client.py",
            "tests/test_document_extractor.py",
            "-v",
            "--tb=short",
        ],
        cwd=cwd,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
