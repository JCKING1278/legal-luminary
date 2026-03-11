/**
 * User Acceptance Testing for production site https://www.legalluminary.com
 * - Verifies _data/important_articles.json is published (featured section and expected titles)
 * - Collects internal links and checks for broken ones; writes broken-links.json for issue creation
 */
import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const PRODUCTION_URL = process.env.PLAYWRIGHT_BASE_URL || 'https://www.legalluminary.com';
const BROKEN_LINKS_OUTPUT = path.join(process.cwd(), 'broken-links.json');

function getExpectedFeaturedTitles(): string[] {
  const dataPath = path.join(process.cwd(), '_data', 'important_articles.json');
  if (!fs.existsSync(dataPath)) return [];
  const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
  const byRel = data?.by_relevance;
  if (!byRel) return [];
  const critical = byRel.critical || [];
  const high = byRel.high || [];
  const featured: string[] = [];
  for (let i = 0; i < 6 && i < critical.length; i++) featured.push(critical[i].title);
  for (let i = featured.length; i < 6 && i - featured.length < high.length; i++) {
    featured.push(high[i - featured.length].title);
  }
  return featured;
}

test.describe('UAT Production', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('production has published important_articles.json', async ({ page }) => {
    const expectedTitles = getExpectedFeaturedTitles();
    if (expectedTitles.length === 0) {
      test.skip(true, 'No _data/important_articles.json or by_relevance data');
      return;
    }
    await page.goto('/', { baseURL: PRODUCTION_URL, waitUntil: 'domcontentloaded' });
    const section = page.locator('.featured-articles-section');
    await expect(section).toBeVisible();
    const heading = page.locator('#featured-articles-title, .featured-articles-section h2');
    await expect(heading).toContainText(/Featured Legal & Election News/i);
    for (const title of expectedTitles) {
      await expect(page.locator('.article-item').filter({ hasText: title })).toBeVisible();
    }
  });

  test('no broken internal links on production', async ({ page, request }) => {
    const baseURL = PRODUCTION_URL;
    const visitedUrls = new Set<string>();
    const linksToCheck = new Map<string, Array<{ sourcePage: string }>>();
    const brokenLinks: Array<{ url: string; status: number; sourcePages: string[] }> = [];

    const normalizeUrl = (url: string): string => {
      try {
        const urlObj = new URL(url, baseURL);
        const pathname = urlObj.pathname === '/' ? '/' : urlObj.pathname.replace(/\/$/, '');
        return `${urlObj.origin}${pathname}${urlObj.search}`;
      } catch {
        return url;
      }
    };

    const isInternalUrl = (url: string): boolean => {
      try {
        const urlObj = new URL(url, baseURL);
        const baseUrlObj = new URL(baseURL);
        return urlObj.origin === baseUrlObj.origin;
      } catch {
        return false;
      }
    };

    const collectLinks = async (pageUrl: string): Promise<void> => {
      const normalized = normalizeUrl(pageUrl);
      if (visitedUrls.has(normalized)) return;
      visitedUrls.add(normalized);

      try {
        const response = await page.goto(pageUrl, {
          baseURL,
          waitUntil: 'domcontentloaded',
          timeout: 15000
        });
        if (!response || response.status() >= 400) return;

        const links = await page.locator('a[href]').all();
        for (const link of links) {
          const href = await link.getAttribute('href');
          if (!href) continue;
          if (href.startsWith('javascript:') || href.startsWith('mailto:') || href.startsWith('tel:')) continue;
          const absoluteUrl = normalizeUrl(href);
          if (!isInternalUrl(absoluteUrl)) continue;
          if (absoluteUrl.includes('#')) {
            const withoutHash = absoluteUrl.split('#')[0];
            if (withoutHash === normalized || withoutHash === `${normalized}/`) continue;
          }
          if (!linksToCheck.has(absoluteUrl)) linksToCheck.set(absoluteUrl, []);
          linksToCheck.get(absoluteUrl)!.push({ sourcePage: normalized });
        }
      } catch {
        // skip page on error
      }
    };

    const commonPages = [
      '/',
      '/about/',
      '/archive/',
      '/resources/',
      '/news-feeds/',
      '/defense/',
      '/personal-injury/',
      '/bell-county/',
      '/texas-law/'
    ];

    for (const pagePath of commonPages) {
      await collectLinks(pagePath);
    }

    for (const [url, infos] of linksToCheck.entries()) {
      try {
        const response = await request.get(url, { timeout: 10000 });
        if (response.status() >= 400) {
          brokenLinks.push({
            url,
            status: response.status(),
            sourcePages: [...new Set(infos.map((i) => i.sourcePage))]
          });
        }
      } catch {
        brokenLinks.push({
          url,
          status: 0,
          sourcePages: [...new Set(infos.map((i) => i.sourcePage))]
        });
      }
    }

    fs.writeFileSync(BROKEN_LINKS_OUTPUT, JSON.stringify(brokenLinks, null, 2), 'utf-8');
    expect(
      brokenLinks.length,
      `Found ${brokenLinks.length} broken link(s). See ${BROKEN_LINKS_OUTPUT} and created GitHub issues.`
    ).toBe(0);
  });
});
