import { defineConfig, devices } from '@playwright/test';
import path from 'path';

/**
 * True E2E Testing Configuration
 *
 * This config sets up dual webServer for:
 * - Django Backend (localhost:8000) with E2E settings
 * - Next.js Frontend (localhost:3000)
 *
 * Screenshots are saved to e2e-screenshots/ folder
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['list']],

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  // Screenshot output directory
  outputDir: path.join(__dirname, 'e2e-screenshots'),

  // Dual webServer configuration for True E2E testing
  webServer: [
    {
      // Django Backend with E2E settings
      command: 'cd ../backend && DJANGO_SETTINGS_MODULE=config.settings.e2e poetry run python manage.py runserver 8000',
      url: 'http://localhost:8000/api/docs/',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
      env: {
        DJANGO_SETTINGS_MODULE: 'config.settings.e2e',
      },
    },
    {
      // Next.js Frontend
      command: 'pnpm dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
      env: {
        NEXT_PUBLIC_API_URL: 'http://localhost:8000/api/v1',
      },
    },
  ],

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
});
