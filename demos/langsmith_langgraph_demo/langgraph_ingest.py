#!/usr/bin/env python3
"""
Simple ingestion helper to load LangGraph dataset JSON and (optionally) push it to a LangGraph API.
This script is resilient: if the `langgraph` package or API key is not available it writes a local copy
and prints the intended API call.
"""
import os
import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "langgraph_datasets" / "pipeline_graph.json"


def load_dataset():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ingest_to_langgraph(dataset: dict):
    try:
        import langgraph
    except Exception:
        print("langgraph SDK not installed. To push the dataset, install the SDK or use the API.")
        print(json.dumps(dataset, indent=2))
        return

    api_key = os.getenv("LANGGRAPH_API_KEY")
    if not api_key:
        print("LANGGRAPH_API_KEY not set; printing dataset instead.")
        print(json.dumps(dataset, indent=2))
        return

    client = langgraph.Client(api_key=api_key)
    # The actual API call depends on the SDK; this is a placeholder illustrating intent.
    try:
        resp = client.create_dataset(name=dataset.get("dataset_name"), payload=dataset)
        print("Uploaded dataset to LangGraph:", resp)
    except Exception as e:
        print("Failed to upload dataset:", e)


def main():
    ds = load_dataset()
    ingest_to_langgraph(ds)


if __name__ == "__main__":
    main()
