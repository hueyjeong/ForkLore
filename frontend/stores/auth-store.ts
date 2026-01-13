import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import * as authApi from '@/lib/api/auth.api';
import type { UserResponse, LoginRequest, SignUpRequest } from '@/types/auth.types';
import { hasTokens } from '@/lib/token';

interface AuthState {
  user: UserResponse | null;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (data: LoginRequest) => Promise<void>;
  signup: (data: SignUpRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  setUser: (user: UserResponse | null) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  devtools(
    (set) => ({
      // 상태
      user: null,
      isLoading: false,
      error: null,

      // 로그인
      login: async (data: LoginRequest) => {
        try {
          set({ isLoading: true, error: null });
          await authApi.login(data);
          
          // 로그인 후 사용자 정보 조회
          const user = await authApi.getMyProfile();
          set({ user, isLoading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : '로그인에 실패했습니다.';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // 회원가입
      signup: async (data: SignUpRequest) => {
        try {
          set({ isLoading: true, error: null });
          await authApi.signup(data);
          set({ isLoading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : '회원가입에 실패했습니다.';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // 로그아웃
      logout: () => {
        authApi.logout();
        set({ user: null, error: null });
      },

      // 사용자 정보 새로고침
      refreshUser: async () => {
        if (!hasTokens()) {
          set({ user: null });
          return;
        }

        try {
          set({ isLoading: true });
          const user = await authApi.getMyProfile();
          set({ user, isLoading: false });
        } catch (error) {
          set({ user: null, isLoading: false });
        }
      },

      // 사용자 설정
      setUser: (user: UserResponse | null) => {
        set({ user });
      },

      // 에러 설정
      setError: (error: string | null) => {
        set({ error });
      },

      // 에러 초기화
      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-store',
    }
  )
);

// 인증 상태 확인 헬퍼
export const useIsAuthenticated = () => {
  const user = useAuthStore((state) => state.user);
  return !!user;
};
