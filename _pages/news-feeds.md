---
permalink: /news-feeds/
layout: default
title: News Feeds (Research)
robots: noindex,nofollow
source_url: "https://www.legalluminary.com/news-feeds/"
verified_at: 2026-02-11
---

# News feeds to consider (research)

This page is a curated list of **RSS/Atom** feeds that may be useful for adding a future “News” or “Government Updates” section. 

**Note:** Some large publishers have limited/blocked RSS access, may require cookies/JS, or may change URLs frequently.

## Local / Central Texas / Bell County area

### KWTX (Waco / Central Texas)
- Homepage: https://www.kwtx.com/
- RSS feeds: (KWTX historically provides RSS but URLs may change; verify latest feed endpoints from their RSS page/search.)

### Killeen Daily Herald
- Homepage: https://kdhnews.com/
- RSS: (Verify; many Lee Enterprises sites have inconsistent RSS availability)

### Temple Daily Telegram
- Homepage: https://www.tdtnews.com/
- RSS: (Verify)

### Austin American-Statesman
- Homepage: https://www.statesman.com/
- RSS: (Often restricted/limited)

## Bell County / City Government (official sources)

### Bell County, Texas (Official site)
- Homepage: https://www.bellcountytx.com/
- Check for “News”, “Press Releases”, or “Agenda” pages; many counties provide updates via CMS without RSS.

### City of Killeen
- Homepage: https://www.killeentexas.gov/

### City of Temple
- Homepage: https://www.templetx.gov/

### City of Belton
- Homepage: https://www.beltontexas.gov/

> For official government sites, if RSS is not available, a future option is to add a lightweight scraper + cache in an external service (not in Jekyll) and display curated headlines.

## Texas Government / Legislature

### Texas Legislature Online
- Homepage: https://capitol.texas.gov/
- RSS/updates: (TLO provides bill updates but RSS availability varies; verify.)

### Office of the Texas Governor
- Homepage: https://gov.texas.gov/
- Look for press release feeds.

### Texas Attorney General (press releases)
- Homepage: https://www.texasattorneygeneral.gov/
- Look for press release feeds.

## National politics / government

### The White House
- Homepage: https://www.whitehouse.gov/
- RSS: Whitehouse.gov has historically provided RSS feeds; verify current feed endpoints.

### U.S. Supreme Court
- Homepage: https://www.supremecourt.gov/
- RSS: SCOTUS provides RSS for opinions and orders in many cases; verify from the site.

### Congress.gov
- Homepage: https://www.congress.gov/
- RSS: Congress.gov provides various RSS feeds (bills, etc.); verify from their RSS documentation.

## Notes on AP / Reuters

- AP RSS endpoints may be blocked/require JS or subscription. Initial quick tests returned “page unavailable” responses, so AP RSS should not be relied on without confirming access.

---

## Next step (if you want these in the UI)
If you want, I can implement a *static* “External News Sources” sidebar widget that simply links to these sources (no RSS fetching), or we can add a separate service (serverless/job) that pulls RSS and outputs a JSON file that Jekyll can render.
