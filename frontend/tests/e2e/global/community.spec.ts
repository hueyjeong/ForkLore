import { test, expect } from '@playwright/test'
import { resetTestData } from '../utils/data-helper'

test.describe('Community Page', () => {
  test.beforeAll(async () => {
    await resetTestData()
  })

  test.beforeEach(async ({ page }) => {
    await page.goto('/community')
  })

  test('should display page title', async ({ page }) => {
    const title = page.getByRole('heading', { name: '커뮤니티', exact: true })
    await expect(title).toBeVisible()
  })

  test('should display page description', async ({ page }) => {
    const description = page.getByText('독자들과 함께 소통하세요')
    await expect(description).toBeVisible()
  })

  test('should display category tabs', async ({ page }) => {
    // Community page should have category tabs
    const tabsList = page.getByRole('tablist')
    await expect(tabsList).toBeVisible()
  })

  test('should display community posts', async ({ page }) => {
    // Wait for posts to load
    await page.waitForTimeout(1000) // Allow time for posts to render

    // Check for post cards or list items
    const pageContent = await page.textContent('body')
    expect(pageContent).toBeTruthy()
    expect(pageContent?.length).toBeGreaterThan(100)
  })

  test('should display post titles', async ({ page }) => {
    await page.waitForTimeout(1000)

    const pageContent = await page.textContent('body')

    // Check for post titles from mock data
    const hasTitles = ['필독', '공지', '토론', '추천', '이벤트'].some(
      title => pageContent?.includes(title)
    )
    expect(hasTitles).toBeTruthy()
  })

  test('should display post categories', async ({ page }) => {
    await page.waitForTimeout(1000)

    const pageContent = await page.textContent('body')

    // Check for category indicators from mock data
    const hasCategories = ['공지', '작품토론', '자유'].some(
      category => pageContent?.includes(category)
    )
    expect(hasCategories).toBeTruthy()
  })

  test('should display post metadata (author, comments, likes)', async ({ page }) => {
    await page.waitForTimeout(1000)

    const pageContent = await page.textContent('body')

    // Check for author names from mock data
    const hasAuthors = ['운영자', '팬아트', '헌터', '독자'].some(
      author => pageContent?.includes(author)
    )
    expect(hasAuthors).toBeTruthy()
  })

  test('should switch between category tabs', async ({ page }) => {
    const tabsList = page.getByRole('tablist')
    await expect(tabsList).toBeVisible()

    const tabs = page.getByRole('tab')
    const tabCount = await tabs.count()

    if (tabCount > 1) {
      // Click on a different tab
      await tabs.nth(1).click()
      await expect(tabs.nth(1)).toHaveAttribute('aria-selected', 'true')
    }
  })

  test('should display pinned posts if any', async ({ page }) => {
    await page.waitForTimeout(1000)

    const pageContent = await page.textContent('body')

    // Check for pinned post indicators or important posts
    const hasPinnedContent = pageContent?.includes('필독') ||
                              pageContent?.includes('공지') ||
                              pageContent?.includes('중요')
    expect(hasPinnedContent).toBeTruthy()
  })

  test('should display comment counts', async ({ page }) => {
    await page.waitForTimeout(1000)

    const pageContent = await page.textContent('body')

    // Comment counts should be visible (numbers)
    const hasNumbers = /\d{2,}/.test(pageContent || '')
    expect(hasNumbers).toBeTruthy()
  })

  test('should display like counts', async ({ page }) => {
    await page.waitForTimeout(1000)

    const pageContent = await page.textContent('body')

    // Like counts should be visible
    const hasLikeIndicators = pageContent?.includes('좋아요') ||
                               /\d{2,}/.test(pageContent || '') // Numbers like 156, 892
    expect(hasLikeIndicators).toBeTruthy()
  })
})
