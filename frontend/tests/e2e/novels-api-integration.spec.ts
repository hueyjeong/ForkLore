import { test, expect } from '@playwright/test';

test.describe('Novels API Integration', () => {
  test('should display novel recommendations on homepage', async ({ page }) => {
    await page.goto('http://localhost:3000');

    const recommendations = page.locator('h2:has-text("맞춤 추천")');
    await expect(recommendations).toBeVisible({ timeout: 10000 });

    const novelLinks = page.locator('a[href^="/novels/"]');
    await expect(novelLinks.first()).toBeVisible();

    const count = await novelLinks.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should display novels on list page', async ({ page }) => {
    await page.goto('http://localhost:3000/novels');

    const title = page.locator('h1:has-text("작품")');
    await expect(title).toBeVisible();

    await page.waitForSelector('[class*="card"]', { timeout: 10000 });

    const cards = page.locator('[class*="card"]');
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);
  });
});
