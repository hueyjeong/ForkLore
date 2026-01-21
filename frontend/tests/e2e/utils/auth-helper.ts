import { Page } from '@playwright/test';

/**
 * 인증된 상태를 시뮬레이션하기 위해 Playwright 페이지 컨텍스트에 인증 쿠키를 추가합니다.
 *
 * 테스트에서 로그인 플로우를 검증하지 않고 인증된 상태가 필요할 때 사용합니다.
 *
 * @param accessToken - 설정할 액세스 토큰 값 (기본값: `'mock-access-token'`)
 * @param refreshToken - 설정할 리프레시 토큰 값 (기본값: `'mock-refresh-token'`)
 */
export async function loginUser(page: Page, accessToken = 'mock-access-token', refreshToken = 'mock-refresh-token') {
  await page.context().addCookies([
    {
      name: 'access_token',
      value: accessToken,
      domain: 'localhost',
      path: '/',
    },
    {
      name: 'refresh_token',
      value: refreshToken,
      domain: 'localhost',
      path: '/',
    },
  ]);
}

/**
 * 현재 Playwright 페이지 컨텍스트의 모든 쿠키를 제거하여 사용자를 로그아웃 상태로 만든다.
 *
 * @param page - 쿠키를 제거할 Playwright `Page` 객체
 */
export async function logoutUser(page: Page) {
  await page.context().clearCookies();
}