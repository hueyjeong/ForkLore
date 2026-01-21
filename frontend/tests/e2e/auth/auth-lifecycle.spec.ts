import { test, expect } from '@playwright/test'
import { LoginPage } from '../pages/login.page'
import { resetTestData, TEST_USERS } from '../utils/data-helper'

test.describe('Authentication Lifecycle', () => {
  let loginPage: LoginPage

  test.beforeAll(async () => {
    await resetTestData()
  })

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page)
  })

  test('Login Flow', async ({ page }) => {
    await loginPage.goto()
    await loginPage.login(TEST_USERS.reader.email, TEST_USERS.reader.password)

    await expect(page).toHaveURL('/')
  })

  test('Protected Route - Unauthenticated', async ({ page }) => {
    await page.goto('/profile')

    await expect(page).toHaveURL(/\/login/)
  })

  test('Session Persistence', async ({ page }) => {
    await loginPage.goto()
    await loginPage.login(TEST_USERS.reader.email, TEST_USERS.reader.password)
    await expect(page).toHaveURL('/')

    await page.goto('/profile')
    await expect(page).toHaveURL('/profile')

    await page.reload()
    await expect(page).toHaveURL('/profile')
  })

  test('Logout', async ({ page }) => {
    await loginPage.goto()
    await loginPage.login(TEST_USERS.reader.email, TEST_USERS.reader.password)
    await expect(page).toHaveURL('/')

    await page.goto('/')

    const userMenuButton = page.locator('button').filter({ has: page.locator('.rounded-full img, .rounded-full svg') }).first()
    await userMenuButton.click()

    const logoutMenuItem = page.getByRole('menuitem', { name: '로그아웃' })
    await logoutMenuItem.click()

    await expect(page).toHaveURL(/\/login/)
  })
})
