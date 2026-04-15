# Design: Jekyll Static Pages Expert Agent

## System Scope
Implement an expert publishing agent in `/Users/sweeden/ll` that ingests research artifacts from `/Users/sweeden/research_paper` and materializes validated Jekyll content plus CI verification hooks.

## Components
1. **Research Input Reader**
   - Reads candidate research and matrix/evidence artifacts from research root.
   - Applies minimal validation for required keys.

2. **Candidate Materializer**
   - Generates `_candidates/<slug>.md` with required front matter:
     - `title`, `city`, `office`, `address`, `candidate_website`, `verification_status`.
   - Renders sections for biography, social links, and news mentions.

3. **Data Sync Writer**
   - Writes `_data/candidates/<city>/<office>/<slug>.json` for template/data-driven pages.

4. **Asset Directory Preparer**
   - Ensures `assets/img/candidates/<slug>/` exists for headshots and derived media.

5. **UI Verification Hook Writer**
   - Writes Selenium case JSON and test file under `tests/selenium`.
   - Cases map each candidate page URL to required text assertions.

6. **GitHub Workflow Integrator**
   - Creates/updates `.github/workflows/candidate-pages-sync.yml`.
   - Workflow stages:
     1. Checkout
     2. Install Ruby + bundle
     3. Install Playwright deps
     4. Build Jekyll
     5. Run Selenium/Playwright verification

## Data Mapping Rules
- Candidate source of truth is research artifacts, not manually edited page body text.
- Missing fields are set to explicit placeholders plus `verification_status: pending`.
- Evidence-backed mentions include source URL and publication metadata.

## Failure Strategy
- If required input files are missing, fail before page generation.
- If Jekyll build fails, workflow exits non-zero.
- If Selenium candidate assertions fail, workflow exits non-zero.

## Operational Commands
- Local generation run:
  - `python /Users/sweeden/ll/scripts/sync_candidates_from_research.py`
- Local smoke:
  - `bundle exec jekyll build`
  - `npx playwright test tests/selenium/test_candidate_pages.py`
