# AGENTS.md - Guide for AI Agents Working with Legal Luminary Jekyll Site

This document provides comprehensive information for AI agents and developers working with the Central Texas Legal Resource Jekyll site, including folder structure, compilation methods, testing procedures, and verification workflows.

## 📁 Jekyll Folder Structure

### Core Jekyll Directories

```
legal-luminary-1/
├── _config.yml              # Jekyll configuration (site settings, navigation, plugins)
├── _layouts/                # Page layout templates
│   ├── default.html         # Main layout (includes header, footer, sidebar)
│   └── m3u8downloader.html  # Special layout for M3U8 downloader page
├── _includes/               # Reusable HTML components
│   ├── ads-defense.html     # Defense attorney sidebar ads
│   ├── ads-injury.html      # Personal injury sidebar ads
│   ├── ads-general.html     # General/homepage sidebar ads
│   ├── ads-home.html        # Homepage-specific ads
│   ├── footer.html          # Site footer component
│   └── sidebar-feed.html    # Sidebar feed component
├── _pages/                  # Static pages (Markdown with front matter)
│   ├── frontpage.md         # Homepage (/)
│   ├── defense.md           # Defense attorneys page (/defense/)
│   ├── personal-injury.md   # Personal injury page (/personal-injury/)
│   ├── texas-law.md         # Texas law information
│   ├── bell-county.md       # Bell County specific info
│   └── [other pages].md
├── _posts/                  # Blog posts (dated Markdown files)
│   └── YYYY-MM-DD-post-title.md
├── assets/                  # Static assets (CSS, JS, images)
│   ├── css/
│   │   └── style.css        # Main stylesheet
│   ├── js/
│   │   ├── main.js          # Main JavaScript
│   │   └── modules/         # ES6 modules
│   └── imgs/                # Images
└── _site/                   # Generated site (build output, gitignored)
```

### Agent Code (.agents/)

```
.agents/
└── legal-luminary/           # Legal document validation agent
    ├── config/
    │   └── settings.py       # Configuration (API keys, trusted domains)
    ├── validators/          # Validation modules
    │   ├── court_doc_validator.py
    │   ├── election_validator.py
    │   ├── judge_validator.py
    │   ├── law_validator.py
    │   ├── news_validator.py
    │   ├── official_validator.py
    │   └── template_validator.py
    ├── experiments/          # Experiment scripts
    ├── tests/                # Unit tests
    ├── pipeline.py           # Main pipeline
    └── state.py              # State management
```

## 🤖 Using the Legal-Luminary Agent

The `.agents/legal-luminary/` directory contains a legal document validation system that verifies the authenticity of legal content including court documents, laws, judges, elections, and officials.

### Trusted Domains

The agent maintains trusted domain lists for validation:
- **Texas Legal Resources**: `texaslawhelp.org`, `texascourthelp.gov`, `texasbar.com`, `edtexweblog.com`
- **Texas Courts**: `texascourthelp.gov`, `txcourts.gov`, `txcourts.net`
- **Law Firms**: Allen & Overy, Clifford Chance, Freshfields, Linklaters, Slaughter and May

### Running the Agent

```bash
# Navigate to agent directory
cd .agents/legal-luminary

# Install dependencies (if needed)
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run pipeline (requires API keys)
python pipeline.py
```

### Configuration

API keys are configured in `.agents/legal-luminary/config/settings.py`:
- `OPENAI_API_KEY`: OpenAI for LLM verification
- `COURTLISTENER_API_KEY`: Court document validation
- `CONGRESS_GOV_API_KEY`: Legislation verification
- `FEC_API_KEY`: Election official verification

### Key Features

- **Court Document Validation**: Verifies real cases via CourtListener API
- **Law Validation**: Confirms statutes exist via Congress.gov
- **Judge Verification**: Validates judges via CourtListener
- **Official Validation**: Checks elected officials via FEC/Congress.gov

### Key Configuration Files

- **`_config.yml`**: Site configuration, navigation, plugins, service area info
- **`Gemfile`**: Ruby dependencies (Jekyll, plugins)
- **`package.json`**: Node.js dependencies (Playwright, TypeScript)
- **`playwright.config.ts`**: Playwright test configuration

## 🔨 Compilation Methods

### Local Development Build

```bash
# Install Ruby dependencies
bundle install

# Build the site (outputs to _site/)
bundle exec jekyll build

# Serve locally with auto-reload (http://127.0.0.1:4000)
bundle exec jekyll serve --livereload --host 127.0.0.1 --port 4000 --baseurl '' --incremental
```

### Using npm Scripts

```bash
# Start Jekyll server (uses package.json script)
npm run jekyll:serve

# Build only (no server)
bundle exec jekyll build
```

### Production Build (GitHub Actions)

The site is automatically built and deployed via GitHub Actions workflow (`.github/workflows/jekyll.yml`). The workflow:
1. Sets up Ruby 3.3
2. Installs dependencies via `bundle install`
3. Builds the site with `bundle exec jekyll build`
4. Deploys to GitHub Pages

### Build Output

- **Destination**: `_site/` directory
- **Base URL**: Configured in `_config.yml` (empty for custom domain, `/repo-name` for project sites)
- **URL**: Set in `_config.yml` (default: `https://www.legalluminary.com`)

## 🧪 Testing with Playwright

### Test Configuration

**File**: `playwright.config.ts`
- **Base URL**: `http://127.0.0.1:4000` (default, configurable via `PLAYWRIGHT_BASE_URL` env var)
- **Test Directory**: `./test_cases` (⚠️ Note: directory is `test_cases`, not `tests`)
- **Timeout**: 30 seconds per test, 10 seconds for expectations

### Running Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all tests (requires Jekyll server running)
npm run test:e2e

# Run tests with UI mode (interactive)
npm run test:e2e:ui

# Run tests in headed mode (see browser)
npm run test:e2e:headed

# Run tests with automatic server start/stop
npm run e2e
```

### Test Files

All test files are located in `./test_cases/` directory:

1. **`test_cases/smoke.spec.ts`**: Basic smoke tests (page loads, navigation, sitemap)
2. **`test_cases/ads-verification.spec.ts`**: Advertisement section verification (see below)
3. **`test_cases/cache-js-files.spec.ts`**: JavaScript file caching tests
4. **`test_cases/mediasite-m3u8.spec.ts`**: M3U8 downloader functionality tests

**⚠️ IMPORTANT**: When creating new tests, place them in `./test_cases/` directory with `.spec.ts` extension.

### Test Structure

Tests use Playwright's test framework with TypeScript:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Test Suite Name', () => {
  test('test name', async ({ page }) => {
    await page.goto('/path');
    await expect(page.locator('selector')).toBeVisible();
  });
});
```

## 🚨 MANDATORY WORKFLOW FOR AI AGENTS

### ⚠️ CRITICAL: Test-First Development Requirement

**ALL AGENTS MUST FOLLOW THIS WORKFLOW BEFORE MAKING ANY CHANGES:**

1. **CREATE PLAYWRIGHT TESTS FIRST** (Test-Driven Development)
   - Before modifying any files, create or update Playwright tests in `test_cases/` that verify the expected behavior
   - Tests should be written to FAIL initially (they test the desired outcome)
   - Place new test files in `./test_cases/` directory
   - Follow existing test patterns in `test_cases/*.spec.ts` files

2. **VERIFY BUILD WORKS** (Before Changes)
   ```bash
   bundle exec jekyll build
   # Must complete without errors
   ```

3. **MAKE CHANGES**
   - Only after tests are written, make the actual code/content changes
   - Follow existing patterns and conventions
   - Maintain third-person wording in all content

4. **VERIFY BUILD AFTER CHANGES**
   ```bash
   bundle exec jekyll build
   # Must complete without errors
   ```

5. **VERIFY WITH LOCAL SERVER**
   ```bash
   bundle exec jekyll serve
   # Manually verify pages load correctly at http://127.0.0.1:4000
   # Stop server when done (Ctrl+C)
   ```

6. **RUN PLAYWRIGHT TESTS**
   ```bash
   npm run e2e
   # All tests should pass, including the new tests you created
   ```

7. **UPDATE CONFIGURATION IF NEEDED**
   - Ensure `package.json` has necessary dependencies
   - Verify `playwright.config.ts` points to `./test_cases` directory
   - Add any new test scripts to `package.json` if needed

8. **DOCUMENT REMAINING TASKS**
   - If unable to complete changes after several attempts, document in `task_progress.md`
   - Include specific error messages, attempted solutions, and next steps

### Workflow Summary

```
1. Write Playwright test → 2. Verify build (before) → 3. Make changes → 
4. Verify build (after) → 5. Verify with serve → 6. Run tests → 
7. Update configs → 8. Document if incomplete
```

**VIOLATION OF THIS WORKFLOW IS NOT ACCEPTABLE.** Tests must be created BEFORE making changes.

## ✅ Verification Workflow

### Pre-Deployment Verification Checklist

1. **Build Verification**
   ```bash
   bundle exec jekyll build
   # Check for errors in output
   ```

2. **Local Server Test**
   ```bash
   bundle exec jekyll serve
   # Manually verify pages load correctly
   ```

3. **Playwright Test Suite**
   ```bash
   npm run e2e
   # All tests should pass
   ```

4. **Advertisement Verification** (see below)

### Advertisement Section Verification

The site includes advertisement sections in the sidebar that must be verified:

#### Advertisement Locations

1. **Homepage** (`/`): General ads (`ads-general.html` or `sidebar_ads_content` in front matter)
2. **Defense Page** (`/defense/`): Defense attorney ads (`ads-defense.html` or `sidebar_ads_content`)
3. **Personal Injury Page** (`/personal-injury/`): Personal injury ads (`ads-injury.html` or `sidebar_ads_content`)

#### Advertisement Structure

Ads are rendered in the sidebar within a `.ad-section` container:
- Each ad is a `.ad-card` element
- Featured ads have class `.ad-card.featured`
- Ads contain:
  - `.ad-specialty`: Service type (e.g., "Criminal Defense", "Personal Injury")
  - `h4`: Attorney/service name
  - `p`: Description
  - `.ad-contact`: Contact information
  - `.ad-cta`: Call-to-action button/link
  - `.ad-disclaimer`: Legal disclaimers (optional)

#### How Ads Are Included

**Method 1: Front Matter (Current Implementation)**
Pages specify ads via `sidebar_ads_content` in front matter:
```yaml
---
layout: default
title: Defense Attorneys
sidebar_ads_content: |
  <div class="ad-card featured">
    <!-- ad content -->
  </div>
---
```

**Method 2: Include Files (Alternative)**
Layout can include ad files based on `sidebar_ads` front matter variable:
```yaml
---
sidebar_ads: defense  # Options: defense, injury, general
---
```

The layout (`_layouts/default.html`) checks for `page.sidebar_ads_content` and renders it in the sidebar.

## 🧪 Advertisement Verification Tests

### Test File: `test_cases/ads-verification.spec.ts`

This test suite verifies that:
1. Advertisement sections appear on the correct pages
2. Ads contain required elements (specialty, name, contact info, CTA)
3. Featured ads are properly marked
4. Ad disclaimers are present where required
5. Ad links are functional

### Running Advertisement Tests

```bash
# Run only ad verification tests
npx playwright test test_cases/ads-verification.spec.ts

# Run with UI mode for debugging
npx playwright test test_cases/ads-verification.spec.ts --ui
```

### Test Coverage

The `ads-verification.spec.ts` test file includes:

1. **Homepage Ad Verification**
   - Verifies `.ad-section` exists in sidebar
   - Checks for "ADVERTISEMENT" label
   - Validates ad cards are present
   - Verifies contact information and CTAs

2. **Defense Page Ad Verification**
   - Verifies defense-specific ads appear
   - Checks for "Criminal Defense" or "Bail Bonds" specialties
   - Validates featured ad is marked correctly

3. **Personal Injury Page Ad Verification**
   - Verifies injury-specific ads appear
   - Checks for "Personal Injury" specialty
   - Validates disclaimers for contingency fee basis

4. **Ad Structure Validation**
   - Ensures all ads have required elements
   - Verifies links are functional
   - Checks for proper ARIA labels

## 🔍 Debugging and Troubleshooting

### Common Issues

1. **Ads Not Appearing**
   - Check `sidebar_ads_content` in page front matter
   - Verify layout includes ad section: `{% if page.sidebar_ads_content %}`
   - Check browser console for JavaScript errors

2. **Build Failures**
   ```bash
   bundle exec jekyll build --trace
   bundle exec jekyll doctor
   ```

3. **Test Failures**
   - Ensure Jekyll server is running on port 4000
   - Check `PLAYWRIGHT_BASE_URL` environment variable
   - Run with `--headed` flag to see browser behavior

4. **Port Conflicts**
   - Change port in `jekyll serve` command
   - Update `PLAYWRIGHT_BASE_URL` accordingly

### Useful Commands

```bash
# Clean build cache
bundle exec jekyll clean

# Rebuild with verbose output
bundle exec jekyll build --trace

# Check Jekyll configuration
bundle exec jekyll doctor

# View Playwright test report
npx playwright show-report
```

## 📝 Content Guidelines for Agents

### Third-Person Wording Requirement

**CRITICAL**: All content must use third-person impersonal wording:
- ✅ Use: "individuals," "clients," "those who," "they," "their"
- ❌ Avoid: "you," "your," "you're"

This is required for compliance and to maintain professional distance.

### Advertisement Content Standards

- All ads must include "ADVERTISEMENT" label
- Attorney ads must include licensing disclaimers
- Contingency fee ads must include fee structure disclaimers
- Contact information must be accurate and functional
- Links must include appropriate `rel` attributes (`sponsored`, `noopener noreferrer`)

### File Modification Guidelines

- **DO NOT** delete or rename existing files
- **DO NOT** change function or class names
- **DO** follow existing patterns when adding content
- **DO** maintain third-person wording throughout

## 🔗 Related Documentation

- **README.md**: General project overview and setup
- **docs/ES6_MODULES_GUIDE.md**: JavaScript module structure
- **docs/PLAYWRIGHT_CACHE_GUIDE.md**: Playwright caching strategies
## 🚀 Quick Reference

### Start Development Environment
```bash
npm run jekyll:serve  # Starts Jekyll on http://127.0.0.1:4000
```

### Run All Tests
```bash
npm run e2e  # Starts server, runs tests, stops server
```

### Verify Ads
```bash
npx playwright test test_cases/ads-verification.spec.ts
```

### Build for Production
```bash
bundle exec jekyll build
# Output in _site/
```

---

**Last Updated**: 2025-01-XX  
**Maintained By**: Cloud Fronts Group  
**For Questions**: See README.md or project documentation

