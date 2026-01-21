import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { UserLoginForm } from './user-login-form'
import { signIn } from "next-auth/react"

// Mock dependencies
vi.mock("next-auth/react", () => ({
  signIn: vi.fn(),
}))

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

const mockLogin = vi.fn()
vi.mock("@/stores/auth-store", () => ({
  useAuthStore: (selector: any) => selector({ login: mockLogin }),
}))

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}))

describe('UserLoginForm Social Login', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders Google and Kakao buttons', () => {
    render(<UserLoginForm />)
    
    expect(screen.getByRole('button', { name: /google/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /kakao/i })).toBeInTheDocument()
  })

  it('calls signIn with google provider when Google button is clicked', async () => {
    render(<UserLoginForm />)
    
    const googleButton = screen.getByRole('button', { name: /google/i })
    fireEvent.click(googleButton)
    
    await waitFor(() => {
      expect(signIn).toHaveBeenCalledWith('google', { callbackUrl: "/" })
    })
  })

  it('calls signIn with kakao provider when Kakao button is clicked', async () => {
    render(<UserLoginForm />)
    
    const kakaoButton = screen.getByRole('button', { name: /kakao/i })
    fireEvent.click(kakaoButton)
    
    await waitFor(() => {
      expect(signIn).toHaveBeenCalledWith('kakao', { callbackUrl: "/" })
    })
  })

  it('shows loading state during social login', async () => {
    // Mock signIn to never resolve immediately to test loading state
    ;(signIn as any).mockImplementation(() => new Promise(() => {}))
    
    render(<UserLoginForm />)
    
    const googleButton = screen.getByRole('button', { name: /google/i })
    fireEvent.click(googleButton)
    
    // Check if the button is disabled
    expect(googleButton).toBeDisabled()
    
    // Check if other buttons are disabled too
    const kakaoButton = screen.getByRole('button', { name: /kakao/i })
    expect(kakaoButton).toBeDisabled()
  })
})
