# Legal Luminary - Central Texas Political Candidate Site

## Project Overview

A professional Jekyll static site for Central Texas (Bell County) political candidates. The site organizes candidates by **jurisdiction/office/role** (incumbent vs challenger), provides navigation with breadcrumbs, and enforces quality standards (headshots, verified sources) before publishing.

## Data Architecture

### Directory Structure
```
_ll/
├── _cities/                    # City jurisdiction pages
│   ├── killeen/
│   │   ├── index.md           # City overview
│   │   ├── mayor/             # Office folder
│   │   │   └── index.md       # Mayor office overview
│   │   └── city-council/      # Office folder
│   │       ├── index.md       # Council overview  
│   │       ├── place-1/
│   │       ├── place-2/
│   │       └── at-large/
│   ├── temple/
│   ├── belton/
│   └── ...
├── _candidates/               # Flat slug-based candidate pages
│   └── {slug}.md              # One file per candidate
├── _data/
│   └── candidates/
│       └── {city}/
│           └── {office}/
│               └── {candidate_slug}.json
└── elections/                  # Elections landing page
    └── index.md              # With breadcrumbs: Home > Elections
```

### Candidate Front Matter Schema
```yaml
---
layout: candidate
title: "Jane Doe"
candidate_slug: "jane_doe"
city: "killeen"
office: "city-council"
office_district: "place-1"
role: "challenger"           # "incumbent" | "challenger"
election_date: "2026-05-02"
headshot_url: "/assets/imgs/candidates/jane_doe/headshot.jpg"  # Required
headshot_verified: true
candidate_website: "https://..."
social_links:
  - { platform: "facebook", url: "..." }
  - { platform: "linkedin", url: "..." }
sources:
  - { type: "city_filing", url: "...", date: "..." }
  - { type: "news", url: "...", publication: "..." }
verification_status: "verified"  # "verified" | "pending" | "draft"
published: true                 # Only publish if verified
---
```

### Publishing Rules
A candidate dossier is published ONLY if:
1. Has a valid headshot image in `/assets/imgs/candidates/{slug}/`
2. Has at least 2 verified sources
3. `verification_status` is "verified"

## Elections Page Requirements

### Breadcrumb Navigation
- Home > Elections > {City} > {Office}
- Each level links to appropriate index page

### Sub-navigation
```
Elections
├── Killeen
│   ├── Mayor
│   ├── City Council
│   │   ├── Place 1
│   │   ├── Place 2
│   │   ├── Place 3
│   │   ├── Place 4
│   │   └── At-Large
│   └── School Board
├── Temple
├── Belton
└── ...
```

### Office Page Components
1. Current elected official (if incumbent)
2. List of challengers with status badges
3. Upcoming election date
4. Link to official city election info
5. Recent news mentions

## Design System

### Color Palette
- Primary: #1a365d (Navy blue - trust/authority)
- Secondary: #2c5282 (Medium blue)
- Accent: #c53030 (Red - urgency/election)
- Background: #f7fafc (Light gray)
- Text: #1a202c (Near black)
- Success: #38a169 (Green - verified)
- Warning: #d69e2e (Yellow - pending)

### Typography
- Headings: "Merriweather" (serif - authority)
- Body: "Source Sans Pro" (sans-serif - readability)
- Monospace: "Source Code Pro" (data/code)

### Component States
- **Verified**: Green badge, published
- **Pending**: Yellow badge, draft mode
- **Missing Info**: Red badge, not published

## Agent Responsibilities

### NewsCrawlerAgent
- Crawls Killeen/Temple/Belton city sites for election news
- Writes posts to `_posts/` with front matter
- Updates `_data/news-feed.json`

### DossierResearchAgent
- Validates candidate headshots exist
- Verifies at least 2 sources per candidate
- Updates `verification_status` in front matter
- Moves incomplete candidates to draft

### WebDesignerAgent
- Generates elections page with breadcrumbs
- Creates office index pages with sub-nav
- Ensures responsive design
- Updates `_data/candidates/` JSON files

### TestAgent
- Validates all candidates have required fields
- Checks headshot file existence
- Verifies breadcrumb structure
- Runs Jekyll build

### UIIntegrationPlaywright
- Checks candidate pages render correctly
- Verifies navigation links work
- Validates responsive breakpoints

## User stories

### US-001: Elections hub with breadcrumbs and sub-navigation

**Priority**: 1  
**Status**: pending  

**User Story**: As a voter I want an Elections area with breadcrumbs and sub-navigation from city through office so I can find races and candidates without hunting unrelated pages.

#### Acceptance Criteria

- [ ] AC-001.1 An elections landing page exists with breadcrumb Home then Elections.
- [ ] AC-001.2 Each city under _cities exposes an index and links to office sections with consistent URL patterns.
- [ ] AC-001.3 Office pages list incumbent versus challenger grouping where applicable and link to candidate dossiers.

### US-002: Publish gates for candidate dossiers

**Priority**: 1  
**Status**: pending  

**User Story**: As an editor I want candidate pages to stay draft until headshot and minimum sources exist so we do not publish incomplete profiles.

#### Acceptance Criteria

- [ ] AC-002.1 Front matter or data files encode headshot path or placeholder policy and at least two cited sources with URL and retrieved date before published true.
- [ ] AC-002.2 Candidates failing gates remain draft or excluded from production collections.
- [ ] AC-002.3 verification_status values are documented and enforced in layouts or generators.

### US-003: Structured candidate data under _data and content trees

**Priority**: 2  
**Status**: pending  

**User Story**: As a maintainer I want candidate JSON and markdown organized by jurisdiction office and role so Jekyll collections and Liquid stay maintainable.

#### Acceptance Criteria

- [ ] AC-003.1 _data candidates mirror the on-disk taxonomy described in Project Overview or successor layout notes.
- [ ] AC-003.2 Slugs are stable URL-safe and unique across the site.
- [ ] AC-003.3 Adding a new candidate follows a documented path in README or AGENTS notes.

### US-004: Election news and dates from allowlisted sources

**Priority**: 2  
**Status**: pending  

**User Story**: As a reader I want recent Central Texas election-related updates with provenance so dates and events stay current without unsourced claims.

#### Acceptance Criteria

- [ ] AC-004.1 News ingest uses only allowlisted RSS official clerk or city URLs or hand-curated bundles committed to the repo.
- [ ] AC-004.2 Posts or feed data include source URL and retrieved timestamp.
- [ ] AC-004.3 Election dates surfaced on hub or office pages match ingested metadata or show unknown explicitly.

### US-005: Green Jekyll build and regression checks

**Priority**: 2  
**Status**: pending  

**User Story**: As a release owner I want jekyll build and scripted checks to pass so broken internal links or missing layouts cannot ship.

#### Acceptance Criteria

- [ ] AC-005.1 bundle exec jekyll build or the repo build script completes without error on a clean checkout after documented setup.
- [ ] AC-005.2 HTML or link checks configured in CI or scripts pass for candidate and elections routes.
- [ ] AC-005.3 sitemap and primary navigation include new elections routes when those pages exist.
