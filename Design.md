# Design: Legal Luminary Jekyll Agent

## System Scope
Build and maintain a Central Texas political candidate site at `/Users/sweeden/ll` that:
1. Organizes candidates by jurisdiction/office/role
2. Enforces publishing quality standards
3. Provides intuitive elections navigation with breadcrumbs

## Directory Structure

### Candidate Files (`_candidates/`)
One markdown file per candidate with complete front matter:
- `candidate_slug`, `city`, `office`, `office_district`
- `role`: `"incumbent"` or `"challenger"`
- `headshot_url`: relative path to image (required for publish)
- `verification_status`: `"verified"` | `"pending"` | `"draft"`
- `published`: boolean (only true if verified)

### City Jurisdiction (`_cities/{city}/`)
```
_cities/
└── {city}/
    ├── index.md              # City overview
    ├── mayor/
    │   └── index.md          # Office overview
    ├── city-council/
    │   ├── index.md          # Office overview
    │   ├── place-1/
    │   ├── place-2/
    │   └── at-large/
    └── school-board/
        └── index.md
```

### Elections Landing Page (`/elections/`)
- Breadcrumb: Home > Elections > {City} > {Office}
- Sub-navigation showing all offices per city
- Links to candidate dossiers

## Components

### 1. BreadcrumbGenerator
Generates breadcrumb HTML from page hierarchy:
```liquid
{% include breadcrumbs.html city="killeen" office="city-council" %}
```

### 2. CandidateDossierGenerator
Creates `_candidates/{slug}.md` with:
- Full front matter from research
- Headshot verification
- Source validation
- `published` flag based on verification

### 3. ElectionsNavBuilder
Creates sub-navigation structure:
- Collapsible city sections
- Office links per city
- Active state highlighting

### 4. DataSyncWriter
Writes `_data/candidates/{city}/{office}/{slug}.json`:
```json
{
  "slug": "jane_doe",
  "city": "killeen",
  "office": "city-council",
  "district": "place-1",
  "role": "challenger",
  "election_date": "2026-05-02",
  "verified": true,
  "headshot": "/assets/imgs/candidates/jane_doe/headshot.jpg"
}
```

### 5. HeadshotValidator
- Checks `/assets/imgs/candidates/{slug}/` directory
- Verifies `headshot.jpg` or `headshot.png` exists
- Updates front matter accordingly

### 6. SourceValidator
- Requires minimum 2 sources per candidate
- Source types: `city_filing`, `news`, `campaign`, `social`
- Updates `verification_status` based on source count

## Publishing Workflow

```
1. NewsCrawlerAgent → _posts/
2. DossierResearchAgent → validate candidates
3. WebDesignerAgent → generate pages
4. HeadshotValidator → check images
5. SourceValidator → check sources
6. Update verification_status
7. Set published=true only if verified
8. TestAgent → run Jekyll build
9. UIIntegrationPlaywright → UI checks
```

## Quality Gates

| Requirement | Gate | Action if Failed |
|------------|------|------------------|
| Headshot exists | HeadshotValidator | Set `published: false` |
| 2+ sources | SourceValidator | Set `verification_status: draft` |
| Valid front matter | SchemaValidator | Block publish |
| Jekyll build passes | TestAgent | Block merge |

## File Naming Conventions

- Cities: lowercase with hyphens (`killeen`, `fort-hood`)
- Offices: lowercase with hyphens (`city-council`, `school-board`)
- Districts: lowercase with hyphens or numbers (`place-1`, `at-large`)
- Candidates: lowercase with underscores (`john_smith`, `jane_doe`)

## Jekyll Collections

```ruby
# _config.yml
collections:
  candidates:
    output: true
    permalink: /candidates/:slug/
  cities:
    output: true
    permalink: /elections/:city/:path/
```

## Multi-Agent Handoff Contract

1. **NewsCrawlerAgent** outputs:
   - `_posts/{date}-{slug}.md`
   - `_data/news-feed.json` (appended)

2. **DossierResearchAgent** outputs:
   - Updated `_candidates/{slug}.md`
   - `_data/candidates/{city}/{office}/validation.json`

3. **WebDesignerAgent** outputs:
   - Elections pages under `/elections/`
   - Updated `_data/candidates/*.json`

4. **TestAgent** outputs:
   - `test-results/build-report.json`
   - `test-results/validation-report.json`

5. **UIIntegrationPlaywright** outputs:
   - `test-results/ui-report.json`
   - Screenshots on failure

## Loopback Integration

After each agent completes:
1. Project Manager updates `tasks.json`
2. Refresh `progress.json`
3. Check if quality gates pass
4. If all gates pass → commit changes
5. If gates fail → create draft PR with issues


## Designer Refinement

- Added orchestration handoff contract for specialist parallel agents.
- Added project-manager feedback checkpoint before next loop iteration.
