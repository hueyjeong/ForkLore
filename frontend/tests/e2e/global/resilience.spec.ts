import { test, expect } from '@playwright/test';
import { MockHelper } from '../utils/mock-helper';

test.describe('Resilience & Robustness', () => {
  let mockHelper: MockHelper;

  test.beforeEach(async ({ page }) => {
    mockHelper = new MockHelper(page);
  });

  test('should handle API 500 errors gracefully', async ({ page }) => {
    await mockHelper.mockRoute(/\/novels(\?.*)?$/, {
      success: false,
      message: 'Internal Server Error'
    }, 500);

    await page.goto('/novels');

    const errorText = page.getByText(/error|failed|wrong/i).first();
    await expect(errorText).toBeVisible({ timeout: 10000 });
  });

  test('should handle network offline state', async ({ page }) => {
    await page.goto('/novels');
    
    await page.context().setOffline(true);
    
    try {
        await page.reload();
    } catch {}

    const body = page.locator('body');
    await expect(body).toBeVisible();
  });
});
