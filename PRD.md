# PRD: Jekyll Static Pages Expert Agent (GitHub Actions)

## Objective
Build a Ralph-compatible expert Jekyll pages agent that consumes verified research artifacts from `/Users/sweeden/research_paper` and publishes candidate pages in `/Users/sweeden/ll`, runnable in GitHub Actions.

## Users
- Site maintainers responsible for publishing candidate pages.
- Research operators who need deterministic, citation-backed site updates.

## Inputs (Authoritative)
- Candidate research output:
  - `/Users/sweeden/adk-ralph/examples/municipal-rnd-assistant-rust/output/candidate_research_loop_output.json`
- Public-records matrix:
  - `/Users/sweeden/research_paper/data/public_records/candidate_lookup_matrix.csv`
  - `/Users/sweeden/research_paper/data/public_records/candidate_lookup_matrix.json`
- Evidence artifacts:
  - `/Users/sweeden/research_paper/data/public_records/evidence/`
- Dossier evidence:
  - `/Users/sweeden/research_paper/dossiers/municipal/<city>/<office>/<candidate_slug>/`

## Outputs (Required)
- Candidate collection pages:
  - `/Users/sweeden/ll/_candidates/<candidate_slug>.md`
- Candidate JSON data:
  - `/Users/sweeden/ll/_data/candidates/<city>/<office>/<candidate_slug>.json`
- Candidate media inventory placeholders:
  - `/Users/sweeden/ll/assets/img/candidates/<candidate_slug>/`
- Selenium verification hooks:
  - `/Users/sweeden/ll/tests/selenium/candidate_ui_cases.json`
  - `/Users/sweeden/ll/tests/selenium/test_candidate_pages.py`
- GitHub Action workflow:
  - `/Users/sweeden/ll/.github/workflows/candidate-pages-sync.yml`

## Functional Requirements
1. Transform research evidence into Jekyll front matter fields (address, biography, social, website, mentions).
2. Keep deterministic slug paths by city/office/candidate.
3. Write/update candidate pages idempotently.
4. Emit UI validation cases from updated candidate set.
5. Add workflow steps to install dependencies, build Jekyll, and run Selenium checks.
6. Fail CI when required candidate fields are missing or page generation fails.

## Quality Requirements
- No candidate page generated without source-backed `mentions` or explicit `verification_status`.
- Preserve existing theme/layout compatibility (`layout: candidate`).
- Workflow must run on `workflow_dispatch` and `push` to main branch.

## Acceptance Criteria
- Candidate pages and data files are updated from research inputs in one run.
- Selenium hook files reflect current candidate inventory.
- GitHub workflow can execute Jekyll build + verification end-to-end.
