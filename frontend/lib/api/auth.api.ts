import { apiClient } from '@/lib/api-client';
import {
  type LoginRequest,
  type SignUpRequest,
  type TokenRefreshRequest,
  type TokenResponse,
  type UserResponse,
  type ApiResponse,
} from '@/types/auth.types';
import { setAccessToken, setRefreshToken, clearTokens } from '@/lib/token';

/**
 * 로그인 API
 */
export async function login(data: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<ApiResponse<TokenResponse>>(
    '/auth/login/',
    data
  );

  // Backend returns 'access' and 'refresh', frontend expects 'access_token' and 'refresh_token' after transformation
  const responseData = response.data.data as unknown as { access: string; refresh: string };
  const accessToken = responseData.access;
  const refreshToken = responseData.refresh;

  // 토큰 저장
  setAccessToken(accessToken);
  setRefreshToken(refreshToken);

  return { accessToken, refreshToken, expiresIn: 3600 };
}

/**
 * 회원가입 API
 */
export async function signup(data: SignUpRequest): Promise<number> {
  const response = await apiClient.post<ApiResponse<number>>(
    '/auth/signup',
    data
  );

  return response.data.data;
}

/**
 * 토큰 갱신 API
 */
export async function refreshToken(
  refreshToken: string
): Promise<TokenResponse> {
  const response = await apiClient.post<ApiResponse<TokenResponse>>(
    '/auth/refresh',
    { refreshToken } as TokenRefreshRequest
  );

  const { accessToken: newAccessToken, refreshToken: newRefreshToken } =
    response.data.data;

  // 새 토큰 저장
  setAccessToken(newAccessToken);
  setRefreshToken(newRefreshToken);

  return response.data.data;
}

/**
 * 내 프로필 조회 API
 */
export async function getMyProfile(): Promise<UserResponse> {
  const response = await apiClient.get<ApiResponse<UserResponse>>('/users/me');
  return response.data.data;
}

/**
 * 로그아웃 (클라이언트 측 토큰 삭제)
 */
export function logout(): void {
  clearTokens();
  // 서버 측 로그아웃 API가 있다면 여기서 호출
}
