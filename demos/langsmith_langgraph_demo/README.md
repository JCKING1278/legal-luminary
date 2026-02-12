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

Validation pipeline and CI
-------------------------

This repository includes a deterministic LangGraph-style pipeline (pipeline.py) that simulates the following nodes: extract, verify (router), generate, evaluate. The pipeline uses `allowlist.json` as the Test Oracle.

Run the pipeline locally using a text file:

```bash
python pipeline.py --file path/to/page_text.txt
```

Or set `SITE_TEXT` and `SITE_URL` environment variables and run without arguments:

```bash
export SITE_TEXT="..."
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

To run the validation pipeline with LangSmith tracing enabled locally:

```bash
export LANGSMITH_API_KEY="sk-..."
export SITE_TEXT="$(cat page_text.txt)"
python pipeline.py
```

The helper writes local records under `demos/langsmith_langgraph_demo/output/langsmith/` when offline or when the SDK is not available.

Pacman RL simulation
---------------------

The Pacman validation simulator models the verification pipeline as an agent collecting "pills" (pages) under `_pages`. Ghosts model intermittent verification failures requiring backtracking. Files included:

- `pacman_env.py` — Gym-like environment implementing pills, ghosts, stay-alive penalty, and verify action.
- `train_pacman.py` — Small Q-learning trainer to explore policies that maximize verification rewards while minimizing stay time and ghost penalties.

Quick run:

```bash
python pacman_env.py  # not executable, import in the trainer
python train_pacman.py --pages 8 --ghost 0.05 --episodes 500
```

The trainer saves a `q_table.json` that can be inspected. This simulator is intentionally simple and designed to be replaced by a more realistic environment that interacts with the actual `_pages` markdown files and the `pipeline.py` verification checks.




