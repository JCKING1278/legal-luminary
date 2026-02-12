# Article Integration Workflow Documentation

## Overview

The article integration system automatically captures approved news articles from verified FCC-licensed broadcast stations and official government sources, validates them against the allowlist, and publishes them as blog posts to the Jekyll site.

## Workflow Pipeline

### 1. **fetch-news-feeds.yml** (Daily at 6:00 AM UTC / 1:00 AM CT)
- Fetches RSS feeds from approved sources
- Updates `_data/news-feed.json` with latest articles
- Commits changes to repository

### 2. **integrate-approved-articles.yml** (Daily at 6:30 AM UTC / 1:30 AM CT)
- Runs 30 minutes after news fetch completes
- Loads allowlist.json v2.1 with 9 FCC-licensed broadcast stations
- Filters articles by approved source domains
- Generates Jekyll blog posts in `_posts/` directory
- Commits new posts to main branch

**Approved Sources:**
- Killeen Police Department (killeenpdnews.com)
- Temple Police Department (city-of-temple.prowly.com)
- KWTB Telemundo (FCC Call Letter 47)
- KVUE News (Austin ABC Affiliate)
- KBTX News (Bryan CBS Affiliate)
- KWBU NPR (FM 103.3, Public Radio)
- Temple Daily Telegram (Bell County local)
- City/County Government Agencies
- Official Legal Resources (Texas AG, Courts)

### 3. **verify-approved-articles.yml** (Triggered on PR/Push)
- Validates all blog posts against allowlist.json
- Checks article format and required front matter
- Performs Jekyll build test with new articles
- Generates integration report

### 4. **jekyll.yml** (Main Deploy Workflow)
- Integrates articles before build
- Verifies markdown traceability
- Builds Jekyll site with all articles
- Deploys to GitHub Pages

## Article Front Matter Format

Each generated blog post includes:

```yaml
---
title: "Article Title"
date: 2026-02-12
layout: default
source_url: "https://original-source.com/article"
source_name: "Source Organization"
verified_at: 2026-02-12
category: news
news_excerpt: true
---
```

## Allowlist v2.1 Specification

### Domains (63 total)
- Government: texasattorneygeneral.gov, bellcountytx.gov, courts.state.tx.us
- News Media: kcen.com, kwtx.com, kxan.com, kwtb.com, kvue.com, kbtx.com, kwbu.org
- Local News: killeendailyherald.com, killeenindependent.com, wacotrib.com, templedailytelegram.com
- Legal Resources: texasbar.com, justia.com, sbot.texas.gov
- *Plus 40+ additional verified sources*

### Social Media Accounts (33 verified)
- Official government Twitter/X accounts
- FCC-licensed broadcast station accounts (KWTB @KWTBTelemundo, KVUE @KVUE, KBTX @KBTXNews, KWBU @KWBUFM)
- Local news organization accounts
- Law enforcement official accounts

### RSS Feeds (15 active)
- KCEN 25 News
- KWTX News
- KXAN News
- KWTB Telemundo
- KVUE News
- KBTX News
- KWBU NPR
- Temple Daily Telegram
- Plus 7 additional official news feeds

## Article Processing Flow

```
News Feed Source
       ↓
Fetch RSS Items
       ↓
Check Domain Against Allowlist v2.1
       ↓
Is Approved? ─→ NO ─→ SKIP
       ↓ YES
Extract Metadata
       ↓
Generate Jekyll Post
       ↓
Write to _posts/YYYY-MM-DD-slug.md
       ↓
Verify Markdown Traceability
       ↓
Build Jekyll Site
       ↓
Deploy to GitHub Pages
       ↓
Article Published
```

## Manual Integration

To manually trigger article integration:

### Via GitHub Actions UI
1. Go to `.github/workflows/integrate-approved-articles.yml`
2. Click "Run workflow"
3. Select branch (main)
4. Click "Run workflow"

### Via Command Line
```bash
# Fetch latest news
bundle exec ruby scripts/fetch-rss-feeds.rb

# Integrate approved articles
python3 scripts/integrate_news_articles.py

# Verify integration
python3 scripts/verify_article_sources.py

# Build and test
bundle exec jekyll build --strict_front_matter

# Commit changes
git add _posts/ _data/
git commit -m "feat: integrate approved news articles from verified sources"
git push origin main
```

## Verification and Validation

All articles go through multi-stage verification:

### 1. Source Verification
- Domain checked against allowlist.json v2.1
- Only articles from approved sources are processed
- FCC call letters verified for broadcast stations

### 2. Content Validation
- Required front matter fields checked
- Article length minimum (50 characters)
- Title length minimum (5 characters)

### 3. Jekyll Build Test
- Site builds successfully with new articles
- No Jekyll warnings or errors
- HTML structure validated

### 4. Markdown Traceability
- Links verified
- References tracked
- Allowlist compliance confirmed

## Configuration Files

### `_data/news-feed.json`
- Central repository of news feed sources
- Updated by fetch-news-feeds.yml
- Contains article items with metadata
- Format: JSON with feeds array

### `demos/langsmith_langgraph_demo/allowlist.json` (v2.1)
- Central source validation authority
- 63 approved domains
- 33 verified social media accounts
- 15 RSS feeds
- 21 contacts
- 5 legal databases
- Updated when new sources are onboarded

### `.github/workflows/integrate-approved-articles.yml`
- Primary integration workflow
- Runs on schedule + manual trigger
- Generates posts from news-feed.json
- Commits directly to main branch

### `.github/workflows/verify-approved-articles.yml`
- Verification and validation workflow
- Runs on PR and article changes
- Used for: source verification, content validation, build testing

## FCC Call Letter Integration

The workflow specifically prioritizes FCC-licensed broadcast stations identified through regulatory research:

### Tier 1: Direct Service (Already Integrated)
- **KCEN 25** (NBC) - kcen.com - @KCEN on Twitter
- **KWTX 10** (ABC) - kwtx.com - @KWTX on Twitter
- **KXAN 36** (NBC Austin) - kxan.com - @KXAN on Twitter

### Tier 2: FCC-Licensed (Added in v2.1)
- **KWTB 47** (Telemundo) - kwtb.com - @KWTBTelemundo on Twitter
- **KVUE 24** (ABC) - kvue.com - @KVUE on Twitter
- **KBTX 3** (CBS) - kbtx.com - @KBTXNews on Twitter
- **KWBU FM 103.3** (NPR) - kwbu.org - @KWBUFM on Twitter

### Supporting Local Sources
- **Temple Daily Telegram** - templedailytelegram.com - Direct Bell County coverage
- **Killeen Police Department** - Official government news
- **Temple Police Department** - Official government news

## Monitoring and Alerts

### Workflow Status
- View integration history: `.github/workflows/integrate-approved-articles.yml` tab
- Check for failures: Actions → integrate-approved-articles → Failed runs
- View article commits: Repository → Commits → [skip ci]

### Integration Metrics
- Posts created per day: Check workflow run artifacts
- Failed verifications: Check logs for "✗ Failed" entries
- Build times: Monitor Jekyll build duration

## Troubleshooting

### Articles Not Appearing
1. Check news-feed.json has items
2. Verify source domain is in allowlist.json
3. Review workflow logs for errors
4. Run verify_article_sources.py manually

### Build Failures
1. Verify Jekyll syntax with `bundle exec jekyll build --strict_front_matter`
2. Check front matter YAML syntax
3. Validate character encoding in article content

### Source Not Approved
1. Add domain to allowlist.json domains array
2. Add social media account to social_media_accounts array
3. Update version number in metadata
4. Commit and push allowlist changes

## Security Considerations

- **Source Validation**: All sources must be in allowlist.json v2.1
- **Content Filtering**: Only articles from approved domains are processed
- **Verification Pipeline**: Articles cannot bypass allowlist checks
- **FCC Verification**: Broadcast stations validated by call letter licensing authority
- **Commit Attribution**: All articles attributed to source with verification timestamp

## Future Enhancements

- [ ] Add support for PDF content extraction
- [ ] Implement category-based article tagging
- [ ] Add natural language content moderation
- [ ] Create topic clustering for related articles
- [ ] Implement duplicate detection
- [ ] Add article ranking by relevance
- [ ] Support for article embargo/scheduling
- [ ] Integration with LangSmith for content evaluation

## References

- **Allowlist Repository**: `demos/langsmith_langgraph_demo/allowlist.json`
- **News Feed Data**: `_data/news-feed.json`
- **Workflow Definitions**: `.github/workflows/`
- **Blog Posts**: `_posts/`
- **Related Documentation**: [AGENTS.md](AGENTS.md), [README.md](README.md)

---

**Last Updated**: February 12, 2026
**Allowlist Version**: v2.1 (FCC Call Letter Integration)
**Status**: ✓ Active and operational
