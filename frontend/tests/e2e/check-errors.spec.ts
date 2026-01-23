import { test } from '@playwright/test';

test('check page errors', async ({ page }) => {
  page.on('console', msg => console.log('[CONSOLE]:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('[PAGE ERROR]:', err.message));
  
  await page.goto('http://localhost:3000/novels');
  await page.waitForTimeout(10000);
  
  const html = await page.content();
  console.log('HTML length:', html.length);
  console.log('Contains grid:', html.includes('grid'));
});
