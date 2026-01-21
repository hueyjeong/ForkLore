/**
 * E2E Test Data Helper
 *
 * Provides utilities for E2E test data management.
 * Calls real Django backend endpoints for True E2E testing.
 */

const E2E_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'
const E2E_RESET_URL = 'http://localhost:8001/api'

interface ResetResponse {
  success: boolean;
  message?: string;
  error?: string;
}

/**
 * Resets the E2E test database and reseeds with fresh test data.
 *
 * This function calls the Django E2E reset endpoint which:
 * 1. Truncates all tables
 * 2. Reseeds with predictable test data
 *
 * Should be called in `beforeAll` or `beforeEach` hooks to ensure test isolation.
 *
 * @throws {Error} If the reset endpoint fails or is not available
 *
 * @example
 * ```typescript
 * import { resetTestData } from '../utils/data-helper';
 *
 * test.describe('My Feature', () => {
 *   test.beforeAll(async () => {
 *     await resetTestData();
 *   });
 *
 *   test('should work with fresh data', async ({ page }) => {
 *     // Test with clean database
 *   });
 * });
 * ```
 */
export async function resetTestData(): Promise<void> {
  const maxRetries = 3
  let lastError: Error | null = null

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(`${E2E_RESET_URL}/e2e/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(
          `Failed to reset E2E test data: ${response.status} ${response.statusText}\n${errorText}`
        )
      }

      const data: ResetResponse = await response.json()

      if (!data.success) {
        throw new Error(`E2E reset failed: ${data.error || 'Unknown error'}`)
      }

      return
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error))
      if (attempt < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, 1000 * attempt))
      }
    }
  }

  throw lastError
}

/**
 * Test user credentials for E2E testing.
 * These match the seed data created by Django's seed_e2e_data command.
 */
export const TEST_USERS = {
  reader: {
    email: 'testreader@example.com',
    password: 'testpassword123',
    nickname: 'TestReader',
  },
  author: {
    email: 'testauthor@example.com',
    password: 'testpassword123',
    nickname: 'TestAuthor',
  },
} as const;

/**
 * Test data identifiers for E2E testing.
 * These match the seed data created by Django's seed_e2e_data command.
 */
export const TEST_DATA = {
  novels: {
    first: 'Test Novel 1',
    count: 50,
  },
  chapters: {
    perBranch: 20,
  },
  branches: {
    perNovel: 1, // main branch guaranteed; forks exist globally (seed contract: 50 main + 20 fork)
  },
} as const;
