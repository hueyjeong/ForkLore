import { describe, it, expect, vi } from 'vitest';
import { login, logout } from '@/lib/api/auth.api';
import { apiClient } from '@/lib/api-client';

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('Auth API', () => {
  it('login should call apiClient.post', async () => {
    const mockResponse = { data: { data: { token: 'fake-token' } } };
    (apiClient.post as any).mockResolvedValue(mockResponse);

    await login({ email: 'test@example.com', password: 'password' });

    expect(apiClient.post).toHaveBeenCalledWith('/auth/login', {
      email: 'test@example.com',
      password: 'password',
    });
  });

  it('logout should call apiClient.post', async () => {
    (apiClient.post as any).mockResolvedValue({});

    await logout();

    expect(apiClient.post).toHaveBeenCalledWith('/auth/logout');
  });
});
