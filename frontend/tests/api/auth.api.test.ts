import { describe, it, expect, vi } from 'vitest';
import { login, logout } from '@/lib/api/auth.api';
import { apiClient } from '@/lib/api-client';
import * as tokenModule from '@/lib/token';

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

vi.mock('@/lib/token', () => ({
  setAccessToken: vi.fn(),
  setRefreshToken: vi.fn(),
  clearTokens: vi.fn(),
}));

describe('Auth API', () => {
  it('login should call apiClient.post', async () => {
    const mockResponse = { data: { data: { accessToken: 'fake-access', refreshToken: 'fake-refresh' } } };
    (apiClient.post as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

    await login({ email: 'test@example.com', password: 'password' });

    expect(apiClient.post).toHaveBeenCalledWith('/auth/login/', {
      email: 'test@example.com',
      password: 'password',
    });
  });

  it('logout should clear tokens', () => {
    logout();

    expect(tokenModule.clearTokens).toHaveBeenCalled();
  });
});
