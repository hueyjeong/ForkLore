import { Page } from '@playwright/test';

/**
 * Set authentication cookies on the given Playwright page to establish an authenticated test state.
 *
 * @param page - Playwright Page whose context will receive the cookies
 * @param accessToken - Value for the `access_token` cookie (default: `'mock-access-token'`)
 * @param refreshToken - Value for the `refresh_token` cookie (default: `'mock-refresh-token'`)
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