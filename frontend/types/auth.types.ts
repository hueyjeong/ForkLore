/**
 * 인증 관련 타입 정의
 * 백엔드 API 스키마와 일치
 */

// 로그인 요청
export interface LoginRequest {
  email: string;
  password: string;
}

// 회원가입 요청
export interface SignUpRequest {
  email: string;
  password: string;
  passwordConfirm: string;
  nickname: string;
  birthDate: string; // YYYY-MM-DD 형식
}

// 토큰 갱신 요청
export interface TokenRefreshRequest {
  refresh: string;
}

// 토큰 응답
export interface TokenResponse {
  access: string;
  refresh: string;
  user?: UserResponse;
}

// 사용자 응답
export interface UserResponse {
  id: number;
  email: string;
  nickname: string;
  profileImageUrl?: string;
  birthDate?: string;
  role: 'READER' | 'AUTHOR' | 'ADMIN';
  authProvider: 'LOCAL' | 'GOOGLE' | 'KAKAO';
}

// API 공통 응답
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  serverTime: string;
}
