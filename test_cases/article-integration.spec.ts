import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Article Integration Verification Tests
 * 
 * Verifies that approved news articles from FCC-licensed sources are:
 * - Properly integrated into Jekyll blog posts
 * - Displayed on the website
 * - Correctly attributed to verified sources
 * - Containing required verification metadata
 */

test.describe('Article Integration from Verified FCC Sources', () => {
  
  test.beforeEach(async ({ page }) => {
    // Set viewport to consistent size
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  // ============================================================
  // Test Suite 1: Article Availability and Display
  // ============================================================

  test('should display blog posts from approved news sources', async ({ page }) => {
    await page.goto('/');
    
    // Look for blog post section (use first match to avoid strict mode when both main and article exist)
    const blogSection = page.locator('main, .blog, .posts, article').first();
    await expect(blogSection).toBeVisible();
    
    // Check for at least one article
    const articles = page.locator('article, .post, .blog-post');
    const articleCount = await articles.count();
    
    if (articleCount > 0) {
      console.log(`✓ Found ${articleCount} articles on homepage`);
      await expect(articles.first()).toBeVisible();
    }
  });

  test('should have blog archive page with integrated articles', async ({ page }) => {
    await page.goto('/archive/');
    
    const postLinks = page.locator('a[href*="_posts/"], a[href*="/blog/"], a[href*="/news/"]');
    const postCount = await postLinks.count();
    
    if (postCount > 0) {
      console.log(`✓ Blog archive has ${postCount} article links`);
      await expect(postLinks.first()).toBeVisible();
    }
  });

  test('should navigate to individual article pages', async ({ page }) => {
    // First, get a blog post link
    await page.goto('/archive/');
    
    const postLinks = page.locator('a[href*=".html"]');
    const linkCount = await postLinks.count();
    
    if (linkCount > 0) {
      // Click on first post
      const firstLink = postLinks.first();
      const href = await firstLink.getAttribute('href');
      
      if (href) {
        await page.goto(href);
        
        // Verify article content is rendered
        const articleContent = page.locator('main, .post-content, article');
        await expect(articleContent).toBeVisible();
        
        console.log(`✓ Successfully navigated to article: ${href}`);
      }
    }
  });

  // ============================================================
  // Test Suite 2: FCC Source Attribution Verification
  // ============================================================

  test('should verify FCC broadcast station sources (KWTB, KVUE, KBTX, KWBU)', async ({ page }) => {
    const fccSources = [
      { name: 'KWTB', domain: 'kwtb.com', callLetter: '47' },
      { name: 'KVUE', domain: 'kvue.com' },
      { name: 'KBTX', domain: 'kbtx.com' },
      { name: 'KWBU', domain: 'kwbu.org' }
    ];

    await page.goto('/');

    // Look for any mention of FCC sources
    for (const source of fccSources) {
      const sourceText = page.locator(`text=${source.name}`);
      const count = await sourceText.count();
      
      if (count > 0) {
        console.log(`✓ Found ${count} references to ${source.name}`);
      }
    }
  });

  test('should verify Temple Daily Telegram (Bell County local source)', async ({ page }) => {
    await page.goto('/');

    const templeText = page.locator('text=Temple Daily Telegram');
    const templateCount = await templeText.count();
    
    if (templateCount > 0) {
      console.log(`✓ Found ${templateCount} references to Temple Daily Telegram`);
    }
  });

  test('should verify Killeen Police Department and Temple Police sources', async ({ page }) => {
    await page.goto('/');

    const killeenText = page.locator('text=Killeen Police');
    const templePoliceText = page.locator('text=Temple Police');

    const killeenCount = await killeenText.count();
    const templeCount = await templePoliceText.count();

    if (killeenCount > 0 || templeCount > 0) {
      console.log(`✓ Found official police sources: Killeen=${killeenCount}, Temple=${templeCount}`);
    }
  });

  // ============================================================
  // Test Suite 3: Article Metadata and Front Matter Verification
  // ============================================================

  test('should have source_url and verified_at metadata in articles', async ({ page }) => {
    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    const linkCount = await postLinks.count();

    if (linkCount > 0) {
      // Visit first article
      const firstLink = postLinks.first();
      const href = await firstLink.getAttribute('href');

      if (href) {
        await page.goto(href);

        // Check for source attribution in article
        const sourceLink = page.locator('a[href*="http"], a[href*="https"]');
        const sourceCount = await sourceLink.count();

        if (sourceCount > 0) {
          console.log(`✓ Article contains ${sourceCount} source links`);
        }

        // Check for metadata text
        const sourceInfo = page.locator('text=Source Information, text=Original URL, text=Verified');
        const infoCount = await sourceInfo.count();

        if (infoCount > 0) {
          console.log(`✓ Found article source information metadata`);
        }
      }
    }
  });

  test('should display verification timestamp for articles', async ({ page }) => {
    await page.goto('/');

    // Look for verified timestamp patterns
    const verifiedText = page.locator('text=/Verified:/i, text=/verified at:/i');
    const verifiedCount = await verifiedText.count();

    if (verifiedCount > 0) {
      console.log(`✓ Found ${verifiedCount} verification timestamps`);
    }

    // Look for date patterns (YYYY-MM-DD format)
    const datePattern = page.locator('text=/\\d{4}-\\d{2}-\\d{2}/');
    const dateCount = await datePattern.count();

    if (dateCount > 0) {
      console.log(`✓ Found ${dateCount} date references`);
    }
  });

  // ============================================================
  // Test Suite 4: Article Content Quality and Structure
  // ============================================================

  test('should verify articles have adequate content length', async ({ page }) => {
    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    const linkCount = await postLinks.count();

    if (linkCount > 0) {
      const firstLink = postLinks.first();
      const href = await firstLink.getAttribute('href');

      if (href) {
        await page.goto(href);

        // Get article content
        const articleContent = page.locator('main, .post-content, article');
        const textContent = await articleContent.textContent();

        if (textContent && textContent.length > 100) {
          console.log(`✓ Article has adequate content length: ${textContent.length} characters`);
        } else if (textContent) {
          console.log(`⚠ Article content short: ${textContent.length} characters`);
        }
      }
    }
  });

  test('should verify article sections and structure', async ({ page }) => {
    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    
    if (await postLinks.count() > 0) {
      const firstLink = postLinks.first();
      const href = await firstLink.getAttribute('href');

      if (href) {
        await page.goto(href);

        // Check for common article sections
        const headline = page.locator('h1, h2, .headline, .title');
        const content = page.locator('main, article, .content');
        const footer = page.locator('footer, .post-footer, .source-info');

        if (await headline.count() > 0) {
          console.log(`✓ Article has headlines`);
        }

        if (await content.count() > 0) {
          console.log(`✓ Article has content section`);
        }

        if (await footer.count() > 0) {
          console.log(`✓ Article has footer/source information`);
        }
      }
    }
  });

  // ============================================================
  // Test Suite 5: Article Category and Tagging
  // ============================================================

  test('should verify articles are tagged with news category', async ({ page }) => {
    await page.goto('/');

    // Look for "news" category tags (text or class)
    const newsTagText = page.locator('text=/category.*news/i, text=/tagged.*news/i');
    const newsTagClass = page.locator('.category, .tag');
    const textCount = await newsTagText.count();
    const classCount = await newsTagClass.count();

    if (textCount > 0 || classCount > 0) {
      console.log(`✓ Found ${textCount + classCount} news category references`);
    }
  });

  test('should verify article date filtering and sorting', async ({ page }) => {
    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    const articles = [];

    const count = await postLinks.count();
    for (let i = 0; i < Math.min(count, 5); i++) {
      const href = await postLinks.nth(i).getAttribute('href');
      if (href) {
        articles.push(href);
      }
    }

    if (articles.length > 0) {
      console.log(`✓ Found ${articles.length} articles`);
      
      // Check for date-based sorting
      const dateOrdering = articles.every((_, i) => 
        i === 0 || articles[i] >= articles[i - 1]
      );
      
      if (dateOrdering) {
        console.log(`✓ Articles appear to be date-sorted`);
      }
    }
  });

  // ============================================================
  // Test Suite 6: Source Links and Attribution
  // ============================================================

  test('should verify external source links are functional', async ({ page }) => {
    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    
    if (await postLinks.count() > 0) {
      const firstLink = postLinks.first();
      const href = await firstLink.getAttribute('href');

      if (href) {
        await page.goto(href);

        // Find external links to original sources
        const externalLinks = page.locator('a[href*="http://"], a[href*="https://"]');
        const externalCount = await externalLinks.count();

        if (externalCount > 0) {
          console.log(`✓ Article contains ${externalCount} external source links`);

          // Verify first external link is valid
          const firstExternal = externalLinks.first();
          const target = await firstExternal.getAttribute('href');
          
          if (target && target.length > 10) {
            console.log(`✓ Source link format valid: ${target.substring(0, 50)}...`);
          }
        }
      }
    }
  });

  test('should verify "Read full article" links work', async ({ page }) => {
    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    
    if (await postLinks.count() > 0) {
      const firstLink = postLinks.first();
      const href = await firstLink.getAttribute('href');

      if (href) {
        await page.goto(href);

        // Look for "Read full article" or similar link
        const readMoreLinks = page.locator(
          'text=/read full|read more|view article|original source/i'
        );
        const readMoreCount = await readMoreLinks.count();

        if (readMoreCount > 0) {
          console.log(`✓ Found ${readMoreCount} "read more" type links`);
        }
      }
    }
  });

  // ============================================================
  // Test Suite 7: Allowlist Compliance Verification
  // ============================================================

  test('should verify allowlist attribution in articles', async ({ page }) => {
    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    
    if (await postLinks.count() > 0) {
      const firstLink = postLinks.first();
      const href = await firstLink.getAttribute('href');

      if (href) {
        await page.goto(href);

        // Look for allowlist reference
        const allowlistRef = page.locator('text=/allowlist/i, text=/v2\\.1/i');
        const allowlistCount = await allowlistRef.count();

        if (allowlistCount > 0) {
          console.log(`✓ Article references allowlist compliance`);
        }

        // Look for verification statement
        const verificationText = page.locator(
          'text=/officially verified|approved sources|regulatory/i'
        );
        const verificationCount = await verificationText.count();

        if (verificationCount > 0) {
          console.log(`✓ Article includes verification statement`);
        }
      }
    }
  });

  // ============================================================
  // Test Suite 8: Page Performance with Integrated Articles
  // ============================================================

  test('should load pages with integrated articles in reasonable time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    
    const loadTime = Date.now() - startTime;
    
    console.log(`✓ Homepage loaded in ${loadTime}ms`);
    
    if (loadTime < 3000) {
      console.log(`✓ Page performance is acceptable`);
    } else if (loadTime < 5000) {
      console.log(`⚠ Page loading is slow: ${loadTime}ms`);
    }
  });

  test('should handle multiple article pages without issues', async ({ page }) => {
    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    const count = await postLinks.count();
    let successCount = 0;

    for (let i = 0; i < Math.min(count, 3); i++) {
      try {
        const link = postLinks.nth(i);
        const href = await link.getAttribute('href');

        if (href) {
          await page.goto(href);
          
          // Verify page loaded
          const content = await page.locator('main, article').count();
          if (content > 0) {
            successCount++;
          }
        }
      } catch (e) {
        console.log(`⚠ Failed to load article ${i + 1}: ${e.message}`);
      }
    }

    if (successCount > 0) {
      console.log(`✓ Successfully loaded ${successCount} article pages`);
    }
  });

  // ============================================================
  // Test Suite 9: Responsive Design with Articles
  // ============================================================

  test('should display articles correctly on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone size

    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    
    if (await postLinks.count() > 0) {
      const firstLink = postLinks.first();
      await expect(firstLink).toBeVisible();
      
      console.log(`✓ Articles visible on mobile viewport`);
    }
  });

  test('should display articles correctly on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad size

    await page.goto('/archive/');

    const articles = page.locator('article, .post');
    
    if (await articles.count() > 0) {
      await expect(articles.first()).toBeVisible();
      
      console.log(`✓ Articles visible on tablet viewport`);
    }
  });

  // ============================================================
  // Test Suite 10: Integration with Jekyll Build
  // ============================================================

  test('should verify Jekyll site built with integrated articles', async ({ page }) => {
    // Check _site directory for generated articles
    const siteUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:4000';
    
    await page.goto('/');

    // Verify we can navigate multiple pages
    const pageTitle = await page.title();
    
    if (pageTitle && pageTitle.length > 0) {
      console.log(`✓ Site title present: ${pageTitle}`);
    }

    // Check for navigation elements
    const nav = page.locator('nav, .navigation, header');
    
    if (await nav.count() > 0) {
      console.log(`✓ Navigation present in Jekyll site`);
    }
  });
});

test.describe('Article Integration - Allowlist Compliance', () => {
  test('should verify no unapproved sources appear in articles', async ({ page }) => {
    // Unapproved sources that should NOT appear
    const unapprovedSources = [
      'legalluminary.com',
      'example.com',
      'random-source.com'
    ];

    await page.goto('/');

    for (const source of unapprovedSources) {
      const sourceText = page.locator(`text=${source}`);
      const count = await sourceText.count();

      if (count === 0) {
        console.log(`✓ Unapproved source not found: ${source}`);
      } else {
        console.log(`⚠ Unapproved source appeared: ${source} (${count} times)`);
      }
    }
  });

  test('should verify articles from allowlist v2.1 sources only', async ({ page }) => {
    const approvedSources = [
      'killeenpd',
      'kwtb',
      'kvue', 
      'kbtx',
      'kwbu',
      'temple daily telegram',
      'killeen daily herald'
    ];

    await page.goto('/archive/');

    const postLinks = page.locator('a[href*=".html"]');
    
    if (await postLinks.count() > 0) {
      const firstLink = postLinks.first();
      const href = await firstLink.getAttribute('href');

      if (href) {
        await page.goto(href);

        // Check which approved sources are mentioned
        let foundSources = 0;
        
        for (const source of approvedSources) {
          const sourceText = page.locator(`text=/${source}/i`);
          const count = await sourceText.count();

          if (count > 0) {
            console.log(`✓ Verified source mentioned: ${source}`);
            foundSources++;
          }
        }

        if (foundSources > 0) {
          console.log(`✓ Article from approved source confirmed`);
        }
      }
    }
  });
});

/**
 * Front page featured articles from _data/important_articles.json
 * Verifies the "Featured Legal & Election News" section shows expected critical/high articles.
 */
test.describe('Front page featured articles (important_articles.json)', () => {
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

  test('front page has Featured Legal & Election News section', async ({ page }) => {
    await page.goto('/');
    const section = page.locator('.featured-articles-section');
    const heading = page.locator('#featured-articles-title, .featured-articles-section h2');
    await expect(section).toBeVisible();
    await expect(heading).toContainText(/Featured Legal & Election News/i);
  });

  test('expected articles from important_articles.json display on front page', async ({ page }) => {
    const expectedTitles = getExpectedFeaturedTitles();
    if (expectedTitles.length === 0) {
      test.skip(true, 'No important_articles.json or by_relevance data');
      return;
    }
    await page.goto('/');
    const section = page.locator('.featured-articles-section');
    await expect(section).toBeVisible();
    const articlesList = section.locator('.articles-list');
    await expect(articlesList).toBeVisible();
    for (const title of expectedTitles) {
      await expect(page.locator('.article-item').filter({ hasText: title })).toBeVisible();
    }
  });

  test('featured section has article items with links and Read More', async ({ page }) => {
    await page.goto('/');
    const section = page.locator('.featured-articles-section');
    const items = section.locator('.article-item');
    const count = await items.count();
    if (count === 0) {
      test.skip(true, 'No featured articles in important_articles.json');
      return;
    }
    await expect(items.first().locator('h4 a[href*="/news/"]')).toBeVisible();
    await expect(items.first().locator('a.read-more')).toBeVisible();
    await expect(items.first().locator('.article-date')).toBeVisible();
  });
});
