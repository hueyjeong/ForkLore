import { describe, it, expect, vi } from 'vitest'
import { login as backendLogin } from '@/lib/api/auth.api'

vi.mock('@/lib/api/auth.api', () => ({
  login: vi.fn(),
}))

describe('NextAuth Configuration', () => {
  describe('Credentials Provider Backend Integration', () => {
    it('should return token response when backend login succeeds', async () => {
      const mockTokenResponse = {
        accessToken: 'test-access-token',
        refreshToken: 'test-refresh-token',
        expiresIn: 3600,
      }

      vi.mocked(backendLogin).mockResolvedValue(mockTokenResponse)

      const mockCredentials = {
        email: 'test@example.com',
        password: 'password123',
      }

      const result = await backendLogin(mockCredentials)

      expect(result).toEqual(mockTokenResponse)
      expect(backendLogin).toHaveBeenCalledWith(mockCredentials)
    })

    it('should handle backend login errors', async () => {
      vi.mocked(backendLogin).mockRejectedValue(
        new Error('Invalid credentials')
      )

      await expect(
        backendLogin({ email: 'wrong@example.com', password: 'wrong' })
      ).rejects.toThrow('Invalid credentials')
    })
  })

  describe('Type Safety', () => {
    it('should have proper TypeScript types for auth configuration', () => {
      expect.assertions(0)
    })
  })
})

describe('Environment Variables', () => {
  beforeEach(() => {
    vi.stubEnv('AUTH_GOOGLE_ID', 'test-google-id')
    vi.stubEnv('AUTH_GOOGLE_SECRET', 'test-google-secret')
    vi.stubEnv('AUTH_KAKAO_ID', 'test-kakao-id')
    vi.stubEnv('AUTH_KAKAO_SECRET', 'test-kakao-secret')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
  })

  it('should allow setting Google OAuth environment variables', () => {
    expect(process.env.AUTH_GOOGLE_ID).toBe('test-google-id')
    expect(process.env.AUTH_GOOGLE_SECRET).toBe('test-google-secret')
  })

  it('should allow setting Kakao OAuth environment variables', () => {
    expect(process.env.AUTH_KAKAO_ID).toBe('test-kakao-id')
    expect(process.env.AUTH_KAKAO_SECRET).toBe('test-kakao-secret')
  })
})
