#!/usr/bin/env python3
"""
Minimal demo that captures a site snapshot, runs a simple LLM evaluation (stub or SDK),
and emits evidence objects. If LangSmith/LangGraph SDKs are installed and configured,
the demo will attempt to call them; otherwise it writes JSON artifacts to ./output.
"""
import os
import sys
import json
import uuid
import hashlib
import datetime
from pathlib import Path

try:
    import requests
except Exception:
    requests = None

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def stub_llm_evaluate(snapshot_text: str, claim: str = "The page supports the claim") -> dict:
    # This is a deterministic, simple stub for demonstration.
    score = 0.5
    if claim.lower() in snapshot_text.lower():
        score = 0.95
    elif any(word in snapshot_text.lower() for word in ["law", "statute", "court"]):
        score = 0.7
    return {
        "summary": f"Score {score:.2f} for claim: {claim}",
        "score": score,
        "model": "stub-1.0"
    }


def fetch_site_text(url: str) -> str:
    if requests is None:
        raise RuntimeError("requests not available; install requirements.txt")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    # Minimal extraction: return raw body text
    return resp.text


def record_local_evidence(evidence: dict) -> Path:
    eid = evidence.get("id") or str(uuid.uuid4())
    path = OUTPUT_DIR / f"evidence-{eid}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    print(f"Wrote evidence to {path}")
    return path


def main():
    site_text = os.getenv("SITE_TEXT")
    site_url = os.getenv("SITE_URL")
    claim = os.getenv("TARGET_CLAIM", "The page supports the stated claim.")

    if not site_text and not site_url:
        print("Set SITE_URL or SITE_TEXT environment variable. Exiting.")
        sys.exit(1)

    if site_url:
        print(f"Fetching {site_url} ...")
        site_text = fetch_site_text(site_url)

    snapshot_hash = compute_hash(site_text)
    snapshot_id = str(uuid.uuid4())
    snapshot = {
        "id": snapshot_id,
        "type": "site_snapshot",
        "timestamp": now_iso(),
        "source": site_url or "inline",
        "sha256": snapshot_hash,
        "content_snippet": site_text[:2000]
    }

    record_local_evidence({
        "id": snapshot_id,
        "role": "snapshot",
        "payload": snapshot,
    })

    # Run (stub) LLM evaluation
    eval_id = str(uuid.uuid4())
    evaluation = stub_llm_evaluate(site_text, claim)
    evidence = {
        "id": eval_id,
        "role": "llm_evaluation",
        "timestamp": now_iso(),
        "target_snapshot": snapshot_id,
        "claim": claim,
        "evaluation": evaluation,
    }

    record_local_evidence(evidence)

    # Emit small verification graph (local JSON)
    graph = {
        "id": str(uuid.uuid4()),
        "created": now_iso(),
        "nodes": [
            {"id": snapshot_id, "type": "snapshot"},
            {"id": eval_id, "type": "evaluation"}
        ],
        "edges": [
            {"from": eval_id, "to": snapshot_id, "label": "evaluates"}
        ]
    }
    record_local_evidence({
        "id": graph["id"],
        "role": "verification_graph",
        "payload": graph,
    })

    print("Demo finished. Artifacts written to ./output/")


if __name__ == "__main__":
    main()
