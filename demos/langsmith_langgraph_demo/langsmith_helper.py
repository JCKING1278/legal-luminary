#!/usr/bin/env python3
"""
Lightweight LangSmith integration helper.

This helper attempts to use the `langsmith` SDK if available. If not, it falls back
to local logging and artifact copying under `demos/langsmith_langgraph_demo/output/langsmith/`.

Functions:
 - create_project(name)
 - start_run(name, project)
 - log_event(run_id, node, payload)
 - upload_artifact(run_id, file_path)

The helper is intentionally defensive so CI can run without an API key.
"""
import os
import json
import uuid
import datetime
from pathlib import Path
import shutil

BASE = Path(__file__).parent
LS_OUTPUT = BASE / "output" / "langsmith"
LS_OUTPUT.mkdir(parents=True, exist_ok=True)

try:
    import langsmith
    HAS_SDK = True
except Exception:
    langsmith = None
    HAS_SDK = False


def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class LangSmithHelper:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("LANGSMITH_API_KEY")
        self.client = None
        if HAS_SDK and self.api_key:
            try:
                # Attempt to construct a LangSmith client; SDKs differ, so be tolerant.
                self.client = langsmith.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def create_project(self, name: str) -> str:
        pid = f"proj-{uuid.uuid4().hex[:8]}"
        meta = {"id": pid, "name": name, "created": now_iso()}
        if self.client:
            try:
                # Placeholder: many SDKs provide a project creation method
                if hasattr(self.client, "create_project"):
                    resp = self.client.create_project(name=name)
                    meta.update({"remote": True, "resp": str(resp)})
                else:
                    meta.update({"remote": False})
            except Exception as e:
                meta.update({"remote": False, "error": str(e)})
        # write local record
        with open(LS_OUTPUT / "project.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        return pid

    def start_run(self, name: str, project: str = None) -> str:
        rid = f"run-{uuid.uuid4().hex[:8]}"
        meta = {"id": rid, "name": name, "project": project, "started": now_iso()}
        with open(LS_OUTPUT / f"run-{rid}.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        return rid

    def log_event(self, run_id: str, node: str, payload: dict):
        entry = {"run": run_id, "node": node, "payload": payload, "ts": now_iso()}
        logp = LS_OUTPUT / "logs.json"
        if logp.exists():
            with open(logp, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(entry)
        with open(logp, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
        # Best-effort SDK call
        if self.client and hasattr(self.client, "log"):
            try:
                self.client.log(run_id=run_id, node=node, payload=payload)
            except Exception:
                pass

    def upload_artifact(self, run_id: str, file_path: str):
        src = Path(file_path)
        if not src.exists():
            return None
        dest_dir = LS_OUTPUT / "artifacts" / run_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        try:
            shutil.copy(src, dest)
        except Exception:
            pass
        # SDK upload attempt (best-effort)
        if self.client and hasattr(self.client, "upload_artifact"):
            try:
                with open(src, "rb") as f:
                    self.client.upload_artifact(run_id=run_id, filename=src.name, content=f.read())
            except Exception:
                pass
        return str(dest)


def default_helper() -> LangSmithHelper:
    return LangSmithHelper()
