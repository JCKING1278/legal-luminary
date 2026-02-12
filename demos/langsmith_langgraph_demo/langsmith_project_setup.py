#!/usr/bin/env python3
"""
Create a LangSmith project record and upload diagram artifacts.

This script uses the `langsmith_helper` to create a project and upload the mermaid
diagram sources as artifacts. It is defensive and will work without network access
by writing local records under `output/langsmith/`.
"""
import os
from pathlib import Path
from .langsmith_helper import default_helper

BASE = Path(__file__).parent
DIAGRAMS = BASE / "diagrams"


def main():
    lsh = default_helper()
    project_id = lsh.create_project("legal-luminary-validation")
    run_id = lsh.start_run("project-setup", project=project_id)
    # upload diagrams
    for p in DIAGRAMS.glob("*.mmd"):
        lsh.upload_artifact(run_id, str(p))
        lsh.log_event(run_id, "artifact_uploaded", {"file": p.name})
    print("Project setup complete. Project id:", project_id, "run id:", run_id)


if __name__ == "__main__":
    main()
