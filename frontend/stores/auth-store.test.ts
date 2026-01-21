import { describe, it, expect, beforeEach, vi } from 'vitest';
import { act } from '@testing-library/react';
import { useAuthStore } from './auth-store';
import * as authApi from '@/lib/api/auth.api';
import * as tokenLib from '@/lib/token';
import type { UserResponse, LoginRequest, SignUpRequest } from '@/types/auth.types';

// Mock API functions
vi.mock('@/lib/api/auth.api', () => ({
  login: vi.fn(),
  signup: vi.fn(),
  getMyProfile: vi.fn(),
  logout: vi.fn(),
}));

// Mock token functions
vi.mock('@/lib/token', () => ({
  hasTokens: vi.fn(),
  setAccessToken: vi.fn(),
  setRefreshToken: vi.fn(),
  clearTokens: vi.fn(),
}));

const mockUser: UserResponse = {
  id: 1,
  email: 'test@example.com',
  nickname: 'TestUser',
  profileImageUrl: 'https://example.com/avatar.jpg',
  birthDate: '1990-01-01',
  role: 'READER',
  authProvider: 'LOCAL',
};

const mockLoginRequest: LoginRequest = {
  email: 'test@example.com',
  password: 'password123',
};

const mockSignupRequest: SignUpRequest = {
  email: 'test@example.com',
  password: 'password123',
  nickname: 'TestUser',
  birthDate: '1990-01-01',
};

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      isLoading: false,
      error: null,
    });

    // Clear all mocks
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should have all actions available', () => {
      const state = useAuthStore.getState();
      expect(typeof state.login).toBe('function');
      expect(typeof state.signup).toBe('function');
      expect(typeof state.logout).toBe('function');
      expect(typeof state.refreshUser).toBe('function');
      expect(typeof state.setUser).toBe('function');
      expect(typeof state.setError).toBe('function');
      expect(typeof state.clearError).toBe('function');
    });
  });

  describe('login action', () => {
    it('should login successfully and set user', async () => {
      vi.mocked(authApi.login).mockResolvedValue({
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        expiresIn: 3600,
      });
      vi.mocked(authApi.getMyProfile).mockResolvedValue(mockUser);

      await act(async () => {
        await useAuthStore.getState().login(mockLoginRequest);
      });

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(authApi.login).toHaveBeenCalledWith(mockLoginRequest);
      expect(authApi.getMyProfile).toHaveBeenCalled();
    });

    it('should set loading state during login', async () => {
      vi.mocked(authApi.login).mockImplementation(
        () => new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              accessToken: 'mock-access-token',
              refreshToken: 'mock-refresh-token',
              expiresIn: 3600,
            });
          }, 100);
        })
      );
      vi.mocked(authApi.getMyProfile).mockResolvedValue(mockUser);

      const loginPromise = act(async () => {
        await useAuthStore.getState().login(mockLoginRequest);
      });

      // Should be loading
      expect(useAuthStore.getState().isLoading).toBe(true);

      await loginPromise;

      // Should finish loading
      expect(useAuthStore.getState().isLoading).toBe(false);
    });

    it('should set error on login failure', async () => {
      const mockError = new Error('Invalid credentials');
      vi.mocked(authApi.login).mockRejectedValue(mockError);
      vi.mocked(authApi.getMyProfile).mockResolvedValue(mockUser);

      await act(async () => {
        await expect(
          useAuthStore.getState().login(mockLoginRequest)
        ).rejects.toThrow('Invalid credentials');
      });

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBe('Invalid credentials');
    });

    it('should set generic error message on non-Error exception', async () => {
      vi.mocked(authApi.login).mockRejectedValue('Network error');
      vi.mocked(authApi.getMyProfile).mockResolvedValue(mockUser);

      await act(async () => {
        await expect(
          useAuthStore.getState().login(mockLoginRequest)
        ).rejects.toEqual('Network error');
      });

      const state = useAuthStore.getState();
      expect(state.error).toBe('로그인에 실패했습니다.');
    });
  });

  describe('signup action', () => {
    it('should signup successfully without setting user', async () => {
      vi.mocked(authApi.signup).mockResolvedValue(1);

      await act(async () => {
        await useAuthStore.getState().signup(mockSignupRequest);
      });

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(authApi.signup).toHaveBeenCalledWith(mockSignupRequest);
    });

    it('should set loading state during signup', async () => {
      vi.mocked(authApi.signup).mockImplementation(
        () => new Promise((resolve) => {
          setTimeout(() => resolve(1), 100);
        })
      );

      const signupPromise = act(async () => {
        await useAuthStore.getState().signup(mockSignupRequest);
      });

      // Should be loading
      expect(useAuthStore.getState().isLoading).toBe(true);

      await signupPromise;

      // Should finish loading
      expect(useAuthStore.getState().isLoading).toBe(false);
    });

    it('should set error on signup failure', async () => {
      const mockError = new Error('Email already exists');
      vi.mocked(authApi.signup).mockRejectedValue(mockError);

      await act(async () => {
        await expect(
          useAuthStore.getState().signup(mockSignupRequest)
        ).rejects.toThrow('Email already exists');
      });

      const state = useAuthStore.getState();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBe('Email already exists');
    });

    it('should set generic error message on non-Error exception', async () => {
      vi.mocked(authApi.signup).mockRejectedValue('Network error');

      await act(async () => {
        await expect(
          useAuthStore.getState().signup(mockSignupRequest)
        ).rejects.toEqual('Network error');
      });

      const state = useAuthStore.getState();
      expect(state.error).toBe('회원가입에 실패했습니다.');
    });
  });

  describe('logout action', () => {
    it('should logout and clear user state', () => {
      // Set initial user state
      useAuthStore.setState({ user: mockUser, error: 'some error' });

      act(() => {
        useAuthStore.getState().logout();
      });

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.error).toBeNull();
      expect(authApi.logout).toHaveBeenCalled();
    });

    it('should call authApi.logout which clears tokens', () => {
      useAuthStore.setState({ user: mockUser });

      act(() => {
        useAuthStore.getState().logout();
      });

      expect(authApi.logout).toHaveBeenCalled();
    });
  });

  describe('refreshUser action', () => {
    it('should refresh user when tokens exist', async () => {
      vi.mocked(tokenLib.hasTokens).mockReturnValue(true);
      vi.mocked(authApi.getMyProfile).mockResolvedValue(mockUser);

      await act(async () => {
        await useAuthStore.getState().refreshUser();
      });

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.isLoading).toBe(false);
      expect(authApi.getMyProfile).toHaveBeenCalled();
    });

    it('should set user to null when no tokens exist', async () => {
      vi.mocked(tokenLib.hasTokens).mockReturnValue(false);

      await act(async () => {
        await useAuthStore.getState().refreshUser();
      });

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(authApi.getMyProfile).not.toHaveBeenCalled();
    });

    it('should handle refresh failure gracefully', async () => {
      vi.mocked(tokenLib.hasTokens).mockReturnValue(true);
      vi.mocked(authApi.getMyProfile).mockRejectedValue(new Error('Unauthorized'));

      await act(async () => {
        await useAuthStore.getState().refreshUser();
      });

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isLoading).toBe(false);
    });

    it('should set loading state during refresh', async () => {
      vi.mocked(tokenLib.hasTokens).mockReturnValue(true);
      vi.mocked(authApi.getMyProfile).mockImplementation(
        () => new Promise((resolve) => {
          setTimeout(() => resolve(mockUser), 100);
        })
      );

      const refreshPromise = act(async () => {
        await useAuthStore.getState().refreshUser();
      });

      // Should be loading
      expect(useAuthStore.getState().isLoading).toBe(true);

      await refreshPromise;

      // Should finish loading
      expect(useAuthStore.getState().isLoading).toBe(false);
    });
  });

  describe('setUser action', () => {
    it('should set user', () => {
      act(() => {
        useAuthStore.getState().setUser(mockUser);
      });

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
    });

    it('should clear user when setting null', () => {
      useAuthStore.setState({ user: mockUser });

      act(() => {
        useAuthStore.getState().setUser(null);
      });

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
    });
  });

  describe('setError action', () => {
    it('should set error', () => {
      act(() => {
        useAuthStore.getState().setError('Test error');
      });

      const state = useAuthStore.getState();
      expect(state.error).toBe('Test error');
    });

    it('should clear error when setting null', () => {
      useAuthStore.setState({ error: 'Existing error' });

      act(() => {
        useAuthStore.getState().setError(null);
      });

      const state = useAuthStore.getState();
      expect(state.error).toBeNull();
    });
  });

  describe('clearError action', () => {
    it('should clear error', () => {
      useAuthStore.setState({ error: 'Some error' });

      act(() => {
        useAuthStore.getState().clearError();
      });

      const state = useAuthStore.getState();
      expect(state.error).toBeNull();
    });
  });

  describe('useIsAuthenticated helper', () => {
    it('should return false when user is null', () => {
      const isAuthenticated = !!useAuthStore.getState().user;
      expect(isAuthenticated).toBe(false);
    });

    it('should return true when user exists', () => {
      useAuthStore.setState({ user: mockUser });
      const isAuthenticated = !!useAuthStore.getState().user;
      expect(isAuthenticated).toBe(true);
    });
  });
});
