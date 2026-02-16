# LangSmith + LangGraph demo

This folder contains a compact, runnable demonstration that captures evidence artifacts from an LLM evaluation of site content and constructs a small verification graph.

Quick steps:

1. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Export credentials (placeholders; do not commit secrets):

```bash
export LANGSMITH_API_KEY="sk-..."
export LANGGRAPH_API_KEY="sk-..."
export SITE_URL="https://www.legalluminary.com/"
```

3. Run the demo:

<!-- Example Node Sequence -->
<MermaidFileLoader file="diagrams/node_sequence.mmd" />

```bash
python demo.py
```
What the demo does:
- Fetches text from `SITE_URL` (or reads `SITE_TEXT` env var).
- Computes a SHA-256 snapshot hash.
- Runs a short LLM evaluation (local client or stub) that judges whether the snapshot supports a target claim.
- Emits evidence objects to a local `output/` folder and (optionally) sends artifacts to LangSmith and LangGraph if their clients are installed and configured.

Notes:
- The demo aims to be portable and self-contained. If `langsmith` or `langgraph` packages are not installed, the demo falls back to writing JSON artifacts to `output/`.
- The demo is intentionally minimal and intended as a starting point for integration into an archival or audit pipeline.

Validation pipeline and CI
-------------------------
This repository includes a deterministic LangGraph-style pipeline (pipeline.py) that simulates the following nodes: extract, verify (router), generate, evaluate. The pipeline uses `allowlist.json` as the Test Oracle.
<!-- Pipeline Flow -->
<MermaidFileLoader file="diagrams/pipeline_flow.mmd" />

Run the pipeline locally using a text file:

```bash
python pipeline.py --file path/to/page_text.txt
```

Or set `SITE_TEXT` and `SITE_URL` environment variables and run without arguments:

```bash
export SITE_TEXT="....new words you expected to appear......"
export SITE_URL="https://www.legalluminary.com"
python pipeline.py
```

GitHub Actions
--------------
The repository contains `.github/workflows/validate.yml` which runs `pipeline.py` for pull requests that touch content. To enable LangSmith tracing in CI, set the `LANGSMITH_API_KEY` secret in the repository settings.

Diagrams and LangGraph datasets
--------------------------------

Mermaid diagram sources are available in `demos/langsmith_langgraph_demo/diagrams/`. Render them locally with any Mermaid renderer or use online renderers. Example files:

- `diagrams/pipeline_flow.mmd` — high-level pipeline flowchart
- `diagrams/node_sequence.mmd` — sequence diagram of node interactions

LangGraph dataset JSON files are in `demos/langsmith_langgraph_demo/langgraph_datasets/`. A helper `langgraph_ingest.py` demonstrates how to load and (optionally) upload datasets to LangGraph. Example usage:

```bash
python langgraph_ingest.py
```

If the `langgraph` SDK is not installed or `LANGGRAPH_API_KEY` is not set, the script will print the dataset to stdout for manual inspection.

LangSmith integration
---------------------

A helper `langsmith_helper.py` provides a defensive integration for emitting traces and artifacts. To enable full LangSmith uploads, set the `LANGSMITH_API_KEY` secret in the environment or in GitHub Secrets and ensure the `langsmith` SDK is installed. Example:

```bash
export LANGSMITH_API_KEY="sk-..."
python langsmith_project_setup.py
```





