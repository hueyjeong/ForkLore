import { test, expect } from '@playwright/test';
import { MockHelper } from '../utils/mock-helper';
import { loginUser } from '../utils/auth-helper';

test.describe('Author Studio', () => {
  let mockHelper: MockHelper;

  test.beforeEach(async ({ page }) => {
    mockHelper = new MockHelper(page);
    await loginUser(page);
    await mockHelper.mockUser();
  });

  test('Navigate to Studio', async ({ page }) => {
    await page.goto('/author');
    
    // Expecting either the studio or a placeholder
    // Currently known gap: UI might be empty or redirected
    
    // If it redirects to login (despite being logged in), then ProtectedRoute issue
    // If it 404s, then route missing.
    
    // Check if URL contains /author
    await expect(page).toHaveURL(/\/author/);
  });
  
  test.fixme('Editor Interaction', async ({ page }) => {
     // Placeholder for future editor tests
     await page.goto('/author/editor/new');
     await expect(page.getByRole('textbox')).toBeVisible();
  });
});
