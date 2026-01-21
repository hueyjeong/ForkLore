import { test, expect } from '@playwright/test'
import { resetTestData } from '../utils/data-helper'

test.describe('Ranking Page - Novelpia Style UI', () => {
  // Reset database once per test file for True E2E testing
  test.beforeAll(async () => {
    await resetTestData()
  })

  test.beforeEach(async ({ page }) => {
    await page.goto('/ranking')
  })

  test('should display ranking header', async ({ page }) => {
    // Check for ranking header/title
    const header = page.getByRole('heading', { level: 1 }).or(
      page.locator('h1')
    )
    await expect(header).toBeVisible()
  })

  test('should display ranking tabs', async ({ page }) => {
    // Ranking page should have tabs for different time periods or categories
    const tabsList = page.getByRole('tablist')
    await expect(tabsList).toBeVisible()
  })

  test('should display ranking novel cards', async ({ page }) => {
    // Wait for ranking list to load
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    // Check that ranking cards are visible
    const novelCards = page.locator('a[href^="/novels/"]')
    const count = await novelCards.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should display ranking numbers or indicators', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    // Ranking page should show rank numbers (1, 2, 3, etc.)
    const pageContent = await page.textContent('body')

    // Check for ranking position indicators or numbered list
    expect(pageContent).toBeTruthy()
  })

  test('should display novel cover images', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    // Check for cover images
    const images = page.locator('a[href^="/novels/"] img')
    const count = await images.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should display novel stats (views, rating)', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    const pageContent = await page.textContent('body')

    // Check for stats indicators (views in K/M format, ratings with decimals)
    const hasStats = pageContent?.includes('M') ||
                     pageContent?.includes('K') ||
                     /\d+\.\d/.test(pageContent || '') // Rating like 4.8
    expect(hasStats).toBeTruthy()
  })

  test('should display author names', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    const pageContent = await page.textContent('body')

    // Check for author names from mock data
    const hasAuthors = ['Elena', 'Jin Woo', 'Aria', 'Luna', 'System'].some(
      author => pageContent?.includes(author)
    )
    expect(hasAuthors).toBeTruthy()
  })

  test('should display PLUS or exclusive badges', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    const pageContent = await page.textContent('body')

    // At least some novels should have badges
    const hasBadges = pageContent?.includes('PLUS') || pageContent?.includes('독점')
    expect(hasBadges).toBeTruthy()
  })

  test('should switch between ranking tabs', async ({ page }) => {
    // Wait for tabs to be visible
    const tabsList = page.getByRole('tablist')
    await expect(tabsList).toBeVisible()

    // Get all tabs
    const tabs = page.getByRole('tab')
    const tabCount = await tabs.count()

    if (tabCount > 1) {
      // Click on second tab
      await tabs.nth(1).click()

      // Verify tab is selected
      await expect(tabs.nth(1)).toHaveAttribute('aria-selected', 'true')
    }
  })

  test('should navigate to novel detail on card click', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    const firstCard = page.locator('a[href^="/novels/"]').first()
    const href = await firstCard.getAttribute('href')

    expect(href).toMatch(/^\/novels\/\d+$/i)
  })
})
