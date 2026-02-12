#!/usr/bin/env python3
"""
LangGraph-style deterministic validation pipeline (simulation).

Nodes:
 1) extract_content
 2) evidence_verification (router)
 3) content_generation
 4) evaluator_node

The pipeline uses a local allowlist (allowlist.json) as the Test Oracle.
It records evidence artifacts to ./output and, if available, pushes traces to LangSmith when
`LANGSMITH_API_KEY` is set and the `langsmith` package is importable.
"""
import os
import json
import uuid
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any

# LangSmith helper
from .langsmith_helper import default_helper

LSH = default_helper()


OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)


def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def compute_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_allowlist() -> Dict[str, Any]:
    p = Path(__file__).parent / "allowlist.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def canonicalize_url(url: str) -> str:
    # Minimal canonicalization for demo purposes
    u = url.strip().lower()
    if u.startswith("http://"):
        u = u[len("http://"):]
    if u.startswith("https://"):
        u = u[len("https://"):]
    if u.endswith("/"):
        u = u[:-1]
    return u


def record(path: Path, data: Dict[str, Any]):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {path}")


class State:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.snapshot = None
        self.verified = False
        self.generated = None
        self.evaluation = None


def node_extract_content(state: State, source_text: str, source_url: str = None):
    snapshot_id = str(uuid.uuid4())
    content_hash = compute_hash(source_text)
    state.snapshot = {
        "id": snapshot_id,
        "text": source_text,
        "url": source_url,
        "sha256": content_hash,
        "timestamp": now_iso(),
    }
    record(OUTPUT / f"snapshot-{snapshot_id}.json", state.snapshot)
    try:
        LSH.log_event(run_id=os.getenv("LS_RUN_ID", "local"), node="extract_content", payload=state.snapshot)
        # upload snapshot artifact
        LSH.upload_artifact(os.getenv("LS_RUN_ID", "local"), str(OUTPUT / f"snapshot-{snapshot_id}.json"))
    except Exception:
        pass
    return state


def node_evidence_verification(state: State, allowlist: Dict[str, Any]):
    url = state.snapshot.get("url") or ""
    domain = canonicalize_url(url)
    allowed = False
    for d in allowlist.get("domains", []):
        if domain == canonicalize_url(d) or domain.endswith("." + canonicalize_url(d)):
            allowed = True
            break
    state.verified = allowed
    evidence = {
        "id": str(uuid.uuid4()),
        "type": "verification",
        "timestamp": now_iso(),
        "snapshot_id": state.snapshot["id"],
        "domain": domain,
        "allowed": allowed,
    }
    record(OUTPUT / f"verification-{evidence['id']}.json", evidence)
    try:
        LSH.log_event(run_id=os.getenv("LS_RUN_ID", "local"), node="evidence_verification", payload=evidence)
        LSH.upload_artifact(os.getenv("LS_RUN_ID", "local"), str(OUTPUT / f"verification-{evidence['id']}.json"))
    except Exception:
        pass
    return state


def node_content_generation(state: State):
    if not state.verified:
        print("Snapshot not verified; halting generation.")
        return state
    # Simple templating for demo
    md = f"---\ntitle: Verified Snapshot from {state.snapshot.get('url')}\n---\n\n"
    md += f"> Source hash: {state.snapshot.get('sha256')}\n\n"
    md += state.snapshot.get("text")[:4000]
    state.generated = {
        "id": str(uuid.uuid4()),
        "path": str(Path("staging") / f"generated-{uuid.uuid4().hex[:8]}.md"),
        "content": md,
        "timestamp": now_iso(),
    }
    out_path = Path(__file__).parent / state.generated["path"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote generated draft to {out_path}")
    record(OUTPUT / f"generated-{state.generated['id']}.json", state.generated)
    try:
        LSH.log_event(run_id=os.getenv("LS_RUN_ID", "local"), node="content_generation", payload={"generated_id": state.generated['id'], "path": state.generated['path']})
        LSH.upload_artifact(os.getenv("LS_RUN_ID", "local"), out_path)
        LSH.upload_artifact(os.getenv("LS_RUN_ID", "local"), str(OUTPUT / f"generated-{state.generated['id']}.json"))
    except Exception:
        pass
    return state


def node_evaluator(state: State, toxicity_threshold: float = 0.8):
    # Deterministic stub evaluator
    content = state.generated.get("content") if state.generated else ""
    score = 0.5
    if "law" in content.lower() or "court" in content.lower():
        score = 0.85
    if len(content) < 20:
        score = 0.2
    toxicity = 0.1 if "offensive" not in content.lower() else 0.95
    ok = (toxicity < toxicity_threshold) and (score >= 0.5)
    state.evaluation = {
        "id": str(uuid.uuid4()),
        "timestamp": now_iso(),
        "score": score,
        "toxicity": toxicity,
        "accepted": ok,
    }
    record(OUTPUT / f"evaluation-{state.evaluation['id']}.json", state.evaluation)
    try:
        LSH.log_event(run_id=os.getenv("LS_RUN_ID", "local"), node="evaluator", payload=state.evaluation)
        LSH.upload_artifact(os.getenv("LS_RUN_ID", "local"), str(OUTPUT / f"evaluation-{state.evaluation['id']}.json"))
    except Exception:
        pass
    return state


def run_pipeline(source_text: str, source_url: str = None):
    allowlist = load_allowlist()
    state = State()
    # Initialize a LangSmith run id and store in env for helper calls
    run_name = f"validation-{uuid.uuid4().hex[:6]}"
    run_id = LSH.start_run(run_name, project="legal-luminary-validation")
    os.environ["LS_RUN_ID"] = run_id
    LSH.log_event(run_id=run_id, node="pipeline_start", payload={"source_url": source_url})
    node_extract_content(state, source_text, source_url)
    node_evidence_verification(state, allowlist)
    if not state.verified:
        print("Verification failed — evidence recorded. Exiting.")
        LSH.log_event(run_id=run_id, node="pipeline_end", payload={"accepted": False, "reason": "verification_failed"})
        return state
    node_content_generation(state)
    node_evaluator(state)
    if state.evaluation and state.evaluation.get("accepted"):
        print("Pipeline accepted generated content — evidence available in output/.")
        LSH.log_event(run_id=run_id, node="pipeline_end", payload={"accepted": True})
    else:
        print("Pipeline rejected generated content — see evaluation evidence in output/.")
        LSH.log_event(run_id=run_id, node="pipeline_end", payload={"accepted": False, "reason": "evaluation_failed"})
    return state


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--url", help="Source URL to fetch (skips network in this demo)")
    p.add_argument("--file", help="Path to local text file to use as source")
    args = p.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
        run_pipeline(text, None)
    elif args.url:
        # For safety the demo does not fetch network by default; allow simple placeholder
        print("Network fetch disabled in demo. Provide --file with the page text or set SITE_TEXT env var.")
    else:
        st = os.getenv("SITE_TEXT")
        if st:
            run_pipeline(st, os.getenv("SITE_URL"))
        else:
            print("Provide --file or set SITE_TEXT environment variable to run the pipeline.")
