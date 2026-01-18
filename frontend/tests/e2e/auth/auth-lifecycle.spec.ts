import { test, expect } from '@playwright/test';
import { MockHelper } from '../utils/mock-helper';
import { LoginPage } from '../pages/login.page';
import { loginUser } from '../utils/auth-helper';

test.describe('Authentication Lifecycle', () => {
  let mockHelper: MockHelper;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    mockHelper = new MockHelper(page);
    loginPage = new LoginPage(page);
  });

  test('Login Flow', async ({ page }) => {
    // Mock 401 initially
    await mockHelper.mockRoute('**/users/me', {}, 401);
    
    // Mock Login Success
    await mockHelper.mockRoute('**/api/auth/login', {
      accessToken: 'mock-access-token',
      refreshToken: 'mock-refresh-token'
    });

    await loginPage.goto();

    // Override /users/me to return success for subsequent requests
    await mockHelper.mockUser();

    await loginPage.login('test@example.com', 'password123');

    // If middleware redirects to login, it might be due to cookie delay.
    // We expect home page.
    await expect(page).toHaveURL('/');
  });

  test('Session Persistence', async ({ page }) => {
    // Inject cookies directly
    await loginUser(page);
    await mockHelper.mockUser();

    await page.goto('/profile');
    await expect(page).toHaveURL('/profile');

    await page.reload();

    await expect(page).toHaveURL('/profile');
  });

  test('Protected Route', async ({ page }) => {
    await mockHelper.mockRoute('**/users/me', {}, 401);

    await page.goto('/profile');

    await expect(page).toHaveURL(/\/login/);
  });

  test('Logout', async ({ page }) => {
    // Inject cookies directly to start as logged in
    await loginUser(page);
    await mockHelper.mockUser();
    await mockHelper.mockRoute('**/api/auth/logout', { success: true });

    await page.goto('/');

    // After logout, /users/me should 401
    await mockHelper.mockRoute('**/users/me', {}, 401);

    const logoutBtn = page.getByRole('button', { name: /logout|로그아웃/i });
    const profileMenu = page.getByRole('button', { name: /profile|user|account|내 정보|mypage|TestReader/i });

    // Handle responsive menu or direct button
    if (await logoutBtn.isVisible()) {
      await logoutBtn.click();
    } else if (await profileMenu.isVisible()) {
      await profileMenu.click();
      await page.getByRole('menuitem', { name: /logout|로그아웃/i }).click();
    } else {
       // Fallback
       await page.getByText(/logout|로그아웃/i).click();
    }

    await expect(page).toHaveURL(/\/login/);
  });
});
