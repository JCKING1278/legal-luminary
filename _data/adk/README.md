# ADK design-patterns workflow data

Outputs from `cargo run -p adk-examples --example design_patterns_workflow` (ADK-Rust).

## Layout

| Path | Purpose |
|------|---------|
| `artifacts/` | `adk-artifact` file-backed blobs (scoped by session/thread) |
| `eval/` | `adk-eval` JSON fixtures (e.g. `collab_graph_smoke.test.json`) |
| `graph_runs/` | Run summaries (`last_graph_run.json`, etc.) |

## Environment

- **`LL_DATA_ROOT`** — use this directory as the root (default when unset: resolve from the example’s `CARGO_MANIFEST_DIR` to `projects/ll/_data/adk`).
- **Ch.16 resource-aware (`design_patterns_workflow`)** — `ADK_RESOURCE_TIER` (`eco` \| `balanced` \| `quality`), `ADK_MODEL_FLASH`, `ADK_MODEL_PRO`.
- **`ADK_DESIGN_PATTERNS_BROWSER=1`** — optional `adk-browser` probe (requires chromedriver + Chrome).
- **`CHROMEDRIVER_PATH`**, **`CHROME_BINARY`**, **`ADK_BROWSER_URL`** — browser session tuning.

This folder is created on first run if it does not exist.
