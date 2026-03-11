# Markdown style guide for `_cities`

This folder uses [markdownlint](https://github.com/DavidAnson/markdownlint) for consistency. Rules that apply (and those relaxed) are below.

## Rules we follow

| Rule | Meaning |
|------|--------|
| **MD022** (blanks-around-headings) | Put one blank line above and below every heading so headings don’t run into content. |
| **MD032** (blanks-around-lists) | Put one blank line before and after a list so lists are visually separated. |
| **MD034** (no-bare-urls) | Use angle brackets around URLs (e.g. `<https://example.com>`) so they’re valid links and not bare text. |
| **MD058** (blanks-around-tables) | Put one blank line before and after tables so they’re clearly separated from headings and paragraphs. |

## Rules relaxed for this folder

| Rule | Meaning | Why relaxed |
|------|--------|-------------|
| **MD010** (no-hard-tabs) | Use spaces instead of tab characters. | We use spaces; config disables this where legacy content had tabs. |
| **MD013** (line-length) | Keep lines ≤ 80 characters. | Long table lines and URLs are acceptable here. |
| **MD041** (first-line-heading) | First line of the file should be a top-level heading. | County overview file may start with a short intro. |
| **MD060** (table-column-style) | Enforce a single table pipe/column style. | Our tables use a consistent style; strict pipe spacing is not required. |

## Quick checklist for new or edited city READMEs

- One blank line after each `## Heading` before the next content.
- One blank line before and after tables and lists.
- Wrap website URLs in angle brackets: `## Website` then a blank line, then `<https://...>`.
- Start the file with `# City Name, Texas - Elected Officials` and use `## City Council`, `## Contact`, `## Website`, `## Notes` (and optional `## Key Staff` / `## Key Appointed Officials`) as needed.
