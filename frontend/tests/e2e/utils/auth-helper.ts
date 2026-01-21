import { Page } from '@playwright/test';

/**
 * Logs in a user by setting authentication cookies directly.
 * Useful for tests that require an authenticated state but don't need to test the login flow itself.
 */
export async function loginUser(page: Page, accessToken = 'mock-access-token', refreshToken = 'mock-refresh-token') {
  await page.context().addCookies([
    {
      name: 'access_token',
      value: accessToken,
      domain: 'localhost',
      path: '/',
    },
    {
      name: 'refresh_token',
      value: refreshToken,
      domain: 'localhost',
      path: '/',
    },
  ]);
}

/**
 * Logs out a user by clearing all cookies.
 */
export async function logoutUser(page: Page) {
  await page.context().clearCookies();
}
