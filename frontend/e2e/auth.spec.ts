import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should handle signup, login, and protected routes correctly', async ({ page }) => {
    const timestamp = Date.now();
    const email = `test_${timestamp}@example.com`;
    const nickname = `User_${timestamp}`;
    const password = 'password123';

    // Mock API
    await page.route('**/api/auth/signup', async route => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ data: 1 }) });
    });
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ data: { accessToken: 'mock-token', refreshToken: 'mock-refresh' } }) });
    });
    await page.route('**/api/users/me', async route => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ data: { email, nickname } }) });
    });

    // 1. Signup Flow
    console.log(`Starting Signup with email: ${email}`);
    await page.goto('/signup');
    
    // Fill form
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="nickname"]', nickname);
    await page.fill('input[name="birthDate"]', '1995-05-20');
    await page.fill('input[name="password"]', password);
    await page.fill('input[name="confirmPassword"]', password);
    
    // Submit
    // Assuming the button has text "회원가입" or type="submit"
    // Use exact text matching for button or accessible role
    const submitButton = page.getByRole('button', { name: "가입하기" });
    await submitButton.click();

    // Verify Redirect to Login (or immediate login if implemented that way, but previous context said redirect)
    // Wait for URL to change to /login
    await expect(page).toHaveURL(/\/login/);
    console.log('Successfully redirected to /login');

    // 2. Login Flow
    console.log('Starting Login');
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    
    await page.click('button[type="submit"]');

    // Verify Redirect to Home
    // Wait for URL to be / (or not login/signup)
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page).not.toHaveURL(/\/signup/);
    console.log('Successfully logged in');

    // 3. Protected Route Verification
    console.log('Verifying Protected Route /profile');
    await page.goto('/profile');
    await expect(page).toHaveURL('/profile');
    console.log('Access to /profile granted');

    // 4. Middleware Verification
    console.log('Verifying Middleware (redirect from /login)');
    await page.goto('/login');
    // Should be redirected back (to home or profile)
    await expect(page).not.toHaveURL(/\/login/);
    console.log('Middleware correctly blocked access to /login for authenticated user');
  });
});
