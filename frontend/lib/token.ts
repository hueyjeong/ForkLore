import { getCookie, setCookie, deleteCookie } from 'cookies-next';

const TOKEN_CONFIG = {
  ACCESS_TOKEN_KEY: 'access_token',
  REFRESH_TOKEN_KEY: 'refresh_token',
  MAX_AGE: 60 * 60 * 24 * 7, // 7일
  PATH: '/',
  SECURE: process.env.NODE_ENV === 'production',
  SAME_SITE: 'lax' as const,
};

/**
 * Access Token 저장
 */
export function setAccessToken(token: string): void {
  setCookie(TOKEN_CONFIG.ACCESS_TOKEN_KEY, token, {
    maxAge: TOKEN_CONFIG.MAX_AGE,
    path: TOKEN_CONFIG.PATH,
    secure: TOKEN_CONFIG.SECURE,
    sameSite: TOKEN_CONFIG.SAME_SITE,
  });
}

/**
 * Refresh Token 저장
 */
export function setRefreshToken(token: string): void {
  setCookie(TOKEN_CONFIG.REFRESH_TOKEN_KEY, token, {
    maxAge: TOKEN_CONFIG.MAX_AGE,
    path: TOKEN_CONFIG.PATH,
    secure: TOKEN_CONFIG.SECURE,
    sameSite: TOKEN_CONFIG.SAME_SITE,
  });
}

/**
 * Access Token 조회
 */
export function getAccessToken(): string | undefined {
  const token = getCookie(TOKEN_CONFIG.ACCESS_TOKEN_KEY);
  return token ? String(token) : undefined;
}

/**
 * Refresh Token 조회
 */
export function getRefreshToken(): string | undefined {
  const token = getCookie(TOKEN_CONFIG.REFRESH_TOKEN_KEY);
  return token ? String(token) : undefined;
}

/**
 * 모든 토큰 삭제
 */
export function clearTokens(): void {
  deleteCookie(TOKEN_CONFIG.ACCESS_TOKEN_KEY, { path: TOKEN_CONFIG.PATH });
  deleteCookie(TOKEN_CONFIG.REFRESH_TOKEN_KEY, { path: TOKEN_CONFIG.PATH });
}

/**
 * 토큰 존재 여부 확인
 */
export function hasTokens(): boolean {
  return !!getAccessToken() && !!getRefreshToken();
}
