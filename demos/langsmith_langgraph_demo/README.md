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
export SITE_URL="https://www.example.com/page-to-verify"
```

3. Run the demo:

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
