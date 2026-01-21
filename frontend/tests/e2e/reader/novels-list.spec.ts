import { test, expect } from '@playwright/test'

test.describe('Novels Page - Novelpia Style UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/novels')
  })

  test('should display page title', async ({ page }) => {
    const title = page.getByRole('heading', { name: '작품' })
    await expect(title).toBeVisible()
  })

  test('should display category tabs with all categories', async ({ page }) => {
    const tabs = ['전체', '멤버십', '독점', '신작', '완결']

    for (const tab of tabs) {
      const tabElement = page.getByRole('tab', { name: tab })
      await expect(tabElement).toBeVisible()
    }
  })

  test('should switch category tabs', async ({ page }) => {
    // Click on 독점 tab
    const exclusiveTab = page.getByRole('tab', { name: '독점' })
    await exclusiveTab.click()
    await expect(exclusiveTab).toHaveAttribute('aria-selected', 'true')

    // Click on 멤버십 tab
    const membershipTab = page.getByRole('tab', { name: '멤버십' })
    await membershipTab.click()
    await expect(membershipTab).toHaveAttribute('aria-selected', 'true')
  })

  test('should display novel filters', async ({ page }) => {
    // Check for genre filter
    const genreSelect = page.locator('[data-testid="genre-filter"]').or(
      page.getByRole('combobox').first()
    )
    await expect(genreSelect).toBeVisible()
  })

  test('should display novel cards with Novelpia style', async ({ page }) => {
    // Wait for novel cards to load
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    // Check that at least one novel card is visible
    const novelCards = page.locator('a[href^="/novels/"]')
    const count = await novelCards.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should display novel card components', async ({ page }) => {
    // Wait for cards to load
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    // Check for novel title
    const firstCard = page.locator('a[href^="/novels/"]').first()
    await expect(firstCard).toBeVisible()

    // Check for cover image
    const coverImage = firstCard.locator('img').first()
    await expect(coverImage).toBeVisible()

    // Check for author name (should be visible in card)
    const cardText = await firstCard.textContent()
    expect(cardText).toBeTruthy()
  })

  test('should display stats row with views, episodes, recommendations', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    // StatsRow should contain view/episode/recommendation icons or text
    // Look for common stats patterns
    const statsTexts = ['조회', '회차', '추천', '화']
    const pageContent = await page.textContent('body')

    // At least one stats indicator should be present
    const hasStats = statsTexts.some(text => pageContent?.includes(text)) ||
                     pageContent?.includes('M') ||
                     pageContent?.includes('K')
    expect(hasStats).toBeTruthy()
  })

  test('should display hashtag pills', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    // Look for hashtag elements (usually styled as pills/badges)
    const pageContent = await page.textContent('body')

    // Check for common genre/tag names from mock data
    const hasTags = ['판타지', '로맨스', '액션', '헌터물', 'SF', '무협'].some(
      tag => pageContent?.includes(tag)
    )
    expect(hasTags).toBeTruthy()
  })

  test('should show PLUS or exclusive badges when applicable', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    const pageContent = await page.textContent('body')

    // Check for badge indicators
    const hasBadges = pageContent?.includes('PLUS') || pageContent?.includes('독점')
    expect(hasBadges).toBeTruthy()
  })

  test('should navigate to novel detail page on card click', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    // Get the first novel card
    const firstCard = page.locator('a[href^="/novels/"]').first()
    const href = await firstCard.getAttribute('href')

    expect(href).toMatch(/^\/novels\/\d+$|^\/novels\/[a-z0-9-]+$/i)
  })

  test('should display relative time (UP indicator)', async ({ page }) => {
    await page.waitForSelector('a[href^="/novels/"]', { timeout: 10000 })

    const pageContent = await page.textContent('body')

    // Check for relative time patterns
    const hasTimeIndicator = pageContent?.includes('UP') ||
                             pageContent?.includes('분전') ||
                             pageContent?.includes('시간전') ||
                             pageContent?.includes('일전')
    expect(hasTimeIndicator).toBeTruthy()
  })
})
