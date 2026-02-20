const { test, expect } = require('@playwright/test');

test.describe('Legal Luminary Smoke Tests', () => {
  test('front page loads successfully', async ({ page }) => {
    await page.goto('https://sweeden-ttu.github.io/legal-luminary/');
    
    // Check page title
    await expect(page).toHaveTitle(/Central Texas Legal/i);
    
    // Check hero section exists
    const hero = page.locator('.hero_title, h1, [class*="hero"]').first();
    await expect(hero).toBeVisible();
  });

  test('recent article section exists and contains content', async ({ page }) => {
    await page.goto('https://sweeden-ttu.github.io/legal-luminary/');
    
            // Check for "Recent Article" heading (exact match to avoid matching "Recent Articles")
            const recentHeading = page.getByRole('heading', { name: 'Recent Article', exact: true });
    await expect(recentHeading).toBeVisible();
    
    // Check that article item exists
    const articleItem = page.locator('.article-item').first();
    await expect(articleItem).toBeVisible();
    
    // Check for article title
    const articleTitle = articleItem.locator('h4 a, h4');
    await expect(articleTitle).toBeVisible();
    
    // Check for article link
    const articleLink = articleItem.locator('a').first();
    const href = await articleLink.getAttribute('href');
    expect(href).toContain('bell-county-legal-resource-center');
  });

  test('recent article link is valid', async ({ page }) => {
    await page.goto('https://sweeden-ttu.github.io/legal-luminary/');
    
    // Get the article link
    const articleLink = page.locator('.article-item a').first();
    const href = await articleLink.getAttribute('href');
    
    // Navigate to the article
    await page.goto(`https://sweeden-ttu.github.io/legal-luminary${href}`);
    
    // Verify article page loads (not 404)
    const title = await page.title();
    expect(title).not.toContain('Not Found');
    expect(title).not.toContain('404');
  });
});
