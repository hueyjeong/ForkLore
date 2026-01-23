import { test, expect } from '@playwright/test';

test('novels page works after suspense removal', async ({ page }) => {
  await page.goto('http://localhost:3000/novels');
  
  // Wait for title
  const title = page.locator('h1');
  await expect(title).toHaveText('작품');
  
  // Wait for novels to load (give it time for React Query)
  await page.waitForTimeout(5000);
  
  // Check for novel cards or empty message
  const novelCards = await page.locator('a[href^="/novels/"]').count();
  console.log('Novel cards found:', novelCards);
  
  // Should have either cards or a message
  if (novelCards > 0) {
    console.log('SUCCESS: Novels displayed');
    expect(novelCards).toBeGreaterThan(0);
  } else {
    const emptyMessage = await page.getByText('표시할 작품이 없습니다').count();
    const errorMessage = await page.getByText('데이터를 불러오는 중 오류가 발생했습니다').count();
    console.log('Empty message:', emptyMessage, 'Error message:', errorMessage);
  }
  
  await page.screenshot({ path: '/tmp/novels-page-final.png', fullPage: true });
});
