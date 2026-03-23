# Legal Luminary — Candidates Page Styleguide

> Reference for LLMs and developers working on the candidates hub.
> Token values live in `_data/design_tokens.yml` and as CSS custom
> properties at the top of `assets/css/candidates-new.css`.

---

## Brand identity

| Attribute     | Value |
|---------------|-------|
| Site name     | Legal Luminary of Central Texas |
| Tagline       | Information - Guidance - Justice |
| Tone          | Authoritative, civic-minded, trustworthy |
| Primary mark  | Scales-of-justice icon + small-caps title |
| Page scope    | Bell County & Central Texas elected offices |

---

## Color system

### Core palette

| Token          | Hex       | Role |
|----------------|-----------|------|
| `--navy-950`   | `#0b1420` | Hub container background (darkest) |
| `--navy-900`   | `#0f172a` | Near-black text, deep fills |
| `--navy-800`   | `#1e293b` | Card headers, strong body text |
| `--navy-700`   | `#334155` | Secondary dark elements |
| `--slate-600`  | `#475569` | Subdued text, eliminated badge |
| `--slate-500`  | `#64748b` | Muted text, labels |
| `--slate-400`  | `#94a3b8` | Secondary text on dark backgrounds |
| `--slate-200`  | `#e2e8f0` | Default border color |
| `--slate-100`  | `#f1f5f9` | Subtle backgrounds, hover states |
| `--slate-50`   | `#f8fafc` | Card/surface white |
| `--gold-600`   | `#c9a227` | Primary gold accent (borders, markers) |
| `--gold-400`   | `#fbbf24` | Bright gold (active tab, hub links) |
| `--blue-600`   | `#2563eb` | Links (light mode), DEM badge |
| `--green-500`  | `#22c55e` | Incumbent status |
| `--red-600`    | `#dc2626` | REP badge, negative finance |

### Usage rules

- The hub container is ALWAYS dark navy (`--navy-950` gradient).
- Cards inside the hub are ALWAYS light (`--slate-50` background).
- Gold is the primary accent. Use `--gold-400` for interactive highlights,
  `--gold-600` for structural markers (border-left on metadata items).
- Blue is for links in light mode ONLY. On the dark hub, links use `--gold-400`.
- Party colors (red/blue/green/purple) appear ONLY inside badge pills.
  Do not use party colors for borders, backgrounds, or structural elements.
- Do not introduce new hues. If a new status or category is needed, use
  a shade from the existing navy/slate/gold scales.

---

## Typography

| Role            | Family     | Size       | Weight | Notes |
|-----------------|------------|------------|--------|-------|
| Page title      | `display`  | 2.25rem    | 700    | Serif. Gold underline on dark. |
| Section heading | `display`  | 1.5rem     | 600    | h2. Border-bottom rule. |
| Office title    | `display`  | 1.4rem     | 700    | h3 inside `.race-header`. |
| Subsection      | `display`  | 1.15rem    | 600    | h3 for Senate/House grouping. |
| Body text       | `body`     | 1rem       | 400    | Sans-serif for readability. |
| Card body       | `body`     | 0.85rem    | 500    | Tighter for cards. |
| Metadata labels | `body`     | 0.68rem    | 700    | ALL CAPS, wide tracking. |
| Badges/chips    | `body`     | 0.65-0.72rem | 700  | ALL CAPS, pill or rounded-rect. |

### Rules

- `display` (serif) is used for headings, titles, and the hub container text.
- `body` (system sans) is used inside cards, metadata panels, badges, and links.
- Never mix: a heading should not use the body font; a card body should not use the display font.
- Minimum readable size is 0.72rem (badges). Do not go smaller.

---

## Component catalog

### Atoms

#### Badge (`.badge`)
Small pill label. Variants:
- `.incumbent-badge` — green gradient, white text. Marks the current officeholder.
- `.party-badge.REP` / `.DEM` / `.GRE` / `.IND` — party-colored gradient.
- `.demo-badge` — slate-600 background, marks sample/placeholder data.
- `.winner-badge` — sky-blue gradient, marks primary winner.
- `.eliminated-badge` — dark slate, strikethrough text.

#### Chip (`.race-chip`)
Inline label on race headers.
- `.race-chip--election` — yellow background, dark text. "Up for election."

#### Election badge (`.election-badge`)
Rounded pill showing election date. Gold gradient in hub context.

#### Social link (`.social-link`)
Small button-like link (FB, IG, LI, Web). Slate background, blue on hover.

#### Headshot / placeholder (`.headshot`, `.headshot-placeholder`)
100x125px rounded rectangle. Placeholder shows first initial on slate gradient.
Challenger variant: 56x70px.

### Molecules

#### Candidate card (`.candidate-card`)
A single candidate's information panel.
- `.candidate-card--featured` — max-width 360px, centered. Solid border.
  Green border when `.incumbent`. Used for the primary officeholder.
- `.candidate-card--challenger` — max-width 240px, dashed border, slate
  background. Smaller headshot, reduced font sizes. Visually subordinate.

Contains: `.card-header` (headshot + badges), `.card-body` (name, position,
term-expires, bio, finance, social links).

#### Office details panel (`.office-details`)
Metadata grid below the race header. Shows term length, election cycle,
jurisdiction, previous holder, salary. Each item has a gold left-border
marker and uppercase label.

### Organisms

#### Race card (`.race-card`)
Full office panel. Contains:
1. `.race-header` — office title (h3) + chips (election status, date badge)
2. `.office-details` — metadata grid
3. `.race-card-body` — featured candidate + challengers section

Light card on dark hub background. Hover lifts with shadow.

#### Tab banner (`.tab-banner`)
Decorative flag element at the top of Federal and State tab panels.
- `.tab-banner--us-flag` — CSS-gradient US flag (stripes + canton with dot stars).
- `.tab-banner--tx-flag` — CSS-gradient Texas flag (blue bar + lone star + white/red).
Opacity 0.42, subtle wave animation, gradient fade to hub background.

#### Municipal city block (`.municipal-city-block`)
Wrapper for a city's races in the Municipal tab. City seal as background
watermark via `--city-seal-url` CSS variable. Currently only Killeen.

#### Tab navigation (`.tab-nav`)
Five tab buttons: Federal, State, County, Municipal, Education.
Each has an SVG icon (`.tab-icon`) and label (`.tab-label`).
Active tab: gold background on dark hub. Keyboard navigable (arrow keys).

#### General election banner (`.general-election-banner`)
Amber/gold alert banner showing election date. Appears in the Federal tab.

### Page-level

#### Candidates hub (`.candidates-hub.candidates-section`)
The full-width dark container that wraps everything. Sets the editorial
serif font, dark navy gradient background, and gold accent scheme.
Hides the site sidebar and recent-articles sections via `body.page-candidates`.

---

## Layout rules

- The hub is full-width (sidebar hidden, container unconstrained).
- Max-width: 1600px on `.candidates-section`, centered.
- Hub inner padding: 2.25rem top, 2rem sides, 2.5rem bottom.
- Cards stack vertically. Featured card centered, challengers in a flex row.
- Office-details grid: `repeat(auto-fill, minmax(220px, 1fr))`.
- Mobile (<=768px): single column, horizontal-scroll tabs, reduced padding.

---

## File map

| File | Purpose |
|------|---------|
| `_candidates/index.md` | Page template — tab structure, race-card includes |
| `_includes/candidates/race-card.html` | Office panel organism |
| `_includes/candidates/candidate-card.html` | Candidate card molecule |
| `_includes/candidates/tab-navigation.html` | Tab bar with SVG icons |
| `_includes/candidates/municipal-by-city.html` | City-grouped municipal races |
| `_data/offices.yml` | Office metadata (title, description, term, etc.) |
| `_data/candidates.yml` | Real candidate data |
| `_data/candidates_placeholders.yml` | Sample data (demo: true) |
| `_data/municipal_hub.yml` | City list for municipal tab |
| `_data/design_tokens.yml` | THIS token reference |
| `assets/css/candidates-new.css` | All styles for the candidates page |
| `design/styleguide.md` | THIS document |

---

## Migration status

CSS custom properties are declared at the top of `candidates-new.css`.
Core hex values are progressively being replaced with `var(--token)` calls.
When editing the CSS, prefer tokens over raw hex. If a value is not yet
tokenized, replace it as part of your edit.
