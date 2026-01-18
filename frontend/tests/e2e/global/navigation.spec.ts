import { test, expect } from '@playwright/test'

test.describe('Navigation and Layout', () => {
  test('should navigate from home to novels page', async ({ page }) => {
    await page.goto('/')

    // Look for navigation link to novels
    const novelsLink = page.getByRole('link', { name: /작품|novels/i }).first()
    await novelsLink.click()

    await expect(page).toHaveURL('/novels')
  })

  test('should navigate from home to ranking page', async ({ page }) => {
    await page.goto('/')

    const rankingLink = page.getByRole('link', { name: /랭킹|ranking/i }).first()
    await rankingLink.click()

    await expect(page).toHaveURL('/ranking')
  })

  test('should navigate from home to community page', async ({ page }) => {
    await page.goto('/')

    const communityLink = page.getByRole('link', { name: /커뮤니티|community/i }).first()
    await communityLink.click()

    await expect(page).toHaveURL('/community')
  })

  test('should maintain consistent layout across pages', async ({ page }) => {
    const pages = ['/novels', '/ranking', '/community']

    for (const path of pages) {
      await page.goto(path)

      // Check for main container
      const main = page.locator('main').first()
      await expect(main).toBeVisible()

      // Check for consistent background
      const background = page.locator('.bg-background').first()
      await expect(background).toBeVisible()
    }
  })

  test('should have responsive layout', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/novels')

    const main = page.locator('main').first()
    await expect(main).toBeVisible()

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 })
    await expect(main).toBeVisible()

    // Test desktop viewport
    await page.setViewportSize({ width: 1280, height: 800 })
    await expect(main).toBeVisible()
  })
})

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should load home page', async ({ page }) => {
    await expect(page).toHaveURL('/')
  })

  test('should display main content', async ({ page }) => {
    const main = page.locator('main').first()
    await expect(main).toBeVisible()
  })

  test('should have navigation header', async ({ page }) => {
    // Look for header or nav element
    const header = page.locator('header').or(page.locator('nav'))
    await expect(header.first()).toBeVisible()
  })
})
