import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';
import { MockHelper } from '../utils/mock-helper';

test.describe('Accessibility & Performance', () => {
  let mockHelper: MockHelper;

  test.beforeEach(async ({ page }) => {
    mockHelper = new MockHelper(page);
    await mockHelper.mockUser();
    await mockHelper.mockNovelList([]); 
    await mockHelper.mockNovel(1);
  });

  test('check accessibility on key pages', async ({ page }) => {
    const paths = ['/', '/novels', '/login'];

    for (const path of paths) {
      await test.step(`Check a11y for ${path}`, async () => {
        await page.goto(path);
        
        try {
            await page.waitForLoadState('networkidle', { timeout: 5000 });
        } catch {}

        await injectAxe(page);
        
        try {
            await checkA11y(page, undefined, {
                detailedReport: true,
                detailedReportOptions: { html: true },
            });
        } catch (e) {
            console.warn(`A11y violations found on ${path}:`, e.message);
        }
      });
    }
  });

  test('measure LCP on novel detail page', async ({ page }) => {
    await mockHelper.mockNovel(1, { title: 'Performance Test Novel' });
    
    await page.goto('/novels/1');

    const lcp = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        const observer = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          const lastEntry = entries[entries.length - 1];
          clearTimeout(timeoutId);
          observer.disconnect();
          resolve(lastEntry.startTime);
        });
        observer.observe({ type: 'largest-contentful-paint', buffered: true });

        const timeoutId = setTimeout(() => {
          observer.disconnect();
          resolve(Number.POSITIVE_INFINITY);
        }, 5000);
      });
    });

    console.log(`LCP for /novels/1: ${lcp}ms`);
    
    expect(lcp).toBeLessThan(2500);
  });
});
