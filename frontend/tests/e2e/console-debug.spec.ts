import { test } from '@playwright/test';

test('check console output', async ({ page }) => {
  page.on('console', msg => {
    if (msg.text().includes('[InfiniteNovelList]')) {
      console.log('>>>', msg.text());
    }
  });
  
  await page.goto('http://localhost:3000/novels');
  await page.waitForTimeout(10000);
});
