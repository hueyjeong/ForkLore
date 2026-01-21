import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;

  constructor(public readonly page: Page) {
    this.emailInput = page.locator('input[id="email"]');
    this.passwordInput = page.locator('input[id="password"]');
    this.loginButton = page.getByRole('button', { name: '로그인', exact: true });
    // Sonner toast or text-destructive error message
    this.errorMessage = page.locator('.text-destructive');
  }

  /**
   * Navigates to the login page.
   */
  async goto() {
    await this.page.goto('/login');
  }

  /**
   * Fills the login form and submits.
   */
  async login(email: string, pass: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(pass);
    await this.loginButton.click();
  }

  /**
   * Asserts that a specific error message is visible.
   */
  async expectError(message: string) {
    // Check either inline error or toast
    // For now assuming inline error text matches
    await expect(this.errorMessage.filter({ hasText: message }).first()).toBeVisible();
  }
}
