import { test, expect } from '@playwright/test';
import { loginUser } from '../utils/auth-helper';

test.describe('Commerce - Subscription', () => {
  test('Subscription Flow (Mocked)', async ({ page }) => {
    // 1. Login
    await loginUser(page);
    // Explicitly mock user with flexible regex to handle potential API prefix issues
    // This ensures we don't get 401/redirected by layout data fetching
    await page.route(/\/users\/me\/?$/, async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                success: true,
                data: {
                    id: 1,
                    email: 'test@example.com',
                    nickname: 'Tester',
                    role: 'READER',
                    authProvider: 'LOCAL'
                },
                serverTime: new Date().toISOString()
            })
        });
    });

    // 2. Initial State: Not Subscribed (404)
    // Using regex to catch API calls regardless of base URL prefix, handling optional trailing slash
    // and ensuring we don't match /subscriptions/checkout
    await page.route(/\/subscriptions\/?(\?.*)?$/, async (route) => {
      // IMPORTANT: Skip document requests to allow page navigation
      if (route.request().resourceType() === 'document') {
        return route.continue();
      }

      if (route.request().method() === 'GET') {
        await route.fulfill({ status: 404, body: JSON.stringify({ message: "Not found" }) });
      } else {
        await route.fallback();
      }
    });

    // 3. Navigate to Subscription Page
    await page.goto('/subscriptions');
    
    // Verify we are on the right page (not redirected to login)
    await expect(page).toHaveURL('/subscriptions');
    await expect(page.getByRole('heading', { name: 'Choose Your Plan' })).toBeVisible();

    // 4. Verify Not Subscribed UI
    // Expect to see pricing cards with "Subscribe" links
    // Use data-testid for stable selection regardless of order
    const premiumSubscribeBtn = page.getByTestId('subscribe-premium');
    await expect(premiumSubscribeBtn).toBeVisible();

    // 5. Setup Success Mock
    const newSubscription: {
      id: number;
      planType: string;
      status: string;
      startedAt: string;
      expiresAt: string;
      cancelledAt: string | null;
      autoRenew: boolean;
      createdAt: string;
    } = {
      id: 1,
      planType: 'PREMIUM',
      status: 'ACTIVE',
      startedAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      cancelledAt: null,
      autoRenew: true,
      createdAt: new Date().toISOString(),
    };

    // Override route to return success for both POST (Create) and GET (Status)
    // Manually mocking to avoid intercepting document navigation
    await page.route(/\/subscriptions\/?(\?.*)?$/, async (route) => {
      if (route.request().resourceType() === 'document') {
        return route.continue();
      }

      const response = {
        success: true,
        data: newSubscription,
        serverTime: new Date().toISOString(),
      };
      
      await route.fulfill({ 
        status: 200, 
        contentType: 'application/json',
        body: JSON.stringify(response) 
      });
    });

    // 6. Start Subscription Flow
    await premiumSubscribeBtn.click();

    // 7. Checkout Page
    await expect(page).toHaveURL(/\/subscriptions\/checkout/);
    
    // 8. Confirm Payment
    // Finding the pay button (usually "Pay $9.99" or similar)
    await page.getByRole('button', { name: /pay/i }).click();

    // 9. Verify Success & Redirect
    // The app should redirect back to /subscriptions
    await expect(page).toHaveURL('/subscriptions');
    
    // 10. Verify Active Subscription UI
    // The page should now display the active subscription details
    await expect(page.getByText('Current Plan', { exact: false })).toBeVisible();
    await expect(page.getByText(/currently subscribed to the premium plan/i)).toBeVisible();
  });
});
