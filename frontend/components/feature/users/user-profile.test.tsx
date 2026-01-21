import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { toast } from 'sonner';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { UserProfile } from './user-profile';
import type { UserResponse } from '@/types/auth.types';
import type { Wallet } from '@/types/wallet.types';

// Mock API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

// Mock the API functions
vi.mock('@/lib/api/auth.api', () => ({
  getMyProfile: vi.fn(),
}));

vi.mock('@/lib/api/wallet.api', () => ({
  getWalletBalance: vi.fn(),
}));

const { getMyProfile } = await import('@/lib/api/auth.api');
const { getWalletBalance } = await import('@/lib/api/wallet.api');

// Mock data fixtures
const mockProfile: UserResponse = {
  id: 1,
  email: 'test@example.com',
  nickname: 'TestUser',
  profileImageUrl: 'https://example.com/avatar.jpg',
  birthDate: '1990-01-01',
  role: 'READER',
  authProvider: 'LOCAL',
};

const mockWallet: Wallet = {
  balance: 1000,
  recent_transactions: [],
};

const createMockResponse = (data: any) => ({
  data: {
    data,
  },
});

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: Infinity,
        staleTime: Infinity,
      },
    },
  });
}

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('UserProfile - useQueries Refactoring', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (getMyProfile as any).mockResolvedValue(mockProfile);
    (getWalletBalance as any).mockResolvedValue(mockWallet);
  });

  it('should fetch profile and wallet data in parallel using useQueries', async () => {
    render(
      <TestWrapper>
        <UserProfile />
      </TestWrapper>
    );

    // Wait for data to load
    await waitFor(async () => {
      const nickname = await screen.findByText('TestUser');
      expect(nickname).toBeInTheDocument();
    });

    // Verify both API calls were made
    expect(getMyProfile).toHaveBeenCalledTimes(1);
    expect(getWalletBalance).toHaveBeenCalledTimes(1);

    // Verify both data sets are rendered
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
    expect(screen.getByText('1,000 C')).toBeInTheDocument();
  });

  it('should show Loader2 spinner while loading', async () => {
    // Make the API calls slow
    (getMyProfile as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockProfile), 100))
    );
    (getWalletBalance as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockWallet), 100))
    );

    render(
      <TestWrapper>
        <UserProfile />
      </TestWrapper>
    );

    // Data should not be visible initially (loading state)
    expect(screen.queryByText('TestUser')).not.toBeInTheDocument();

    // Loading container should be visible
    const loadingContainer = document.querySelector('.animate-spin');
    expect(loadingContainer).toBeInTheDocument();

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('TestUser')).toBeInTheDocument();
    });
  });

  it('should show toast error on API failure', async () => {
    const toastSpy = vi.spyOn(toast, 'error');

    (getMyProfile as any).mockRejectedValue(new Error('API Error'));

    render(
      <TestWrapper>
        <UserProfile />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(toastSpy).toHaveBeenCalledWith('Failed to load profile data');
    });
  });

  it('should render wallet balance correctly', async () => {
    const walletWithBalance: Wallet = {
      balance: 50000,
      recent_transactions: [],
    };

    (getWalletBalance as any).mockResolvedValue(walletWithBalance);

    render(
      <TestWrapper>
        <UserProfile />
      </TestWrapper>
    );

    await waitFor(async () => {
      const balance = await screen.findByText('50,000 C');
      expect(balance).toBeInTheDocument();
    });
  });

  it('should render profile information correctly', async () => {
    const profileWithImage: UserResponse = {
      ...mockProfile,
      nickname: 'ImageUser',
      profileImageUrl: 'https://example.com/avatar2.jpg',
      role: 'AUTHOR',
    };

    (getMyProfile as any).mockResolvedValue(profileWithImage);

    render(
      <TestWrapper>
        <UserProfile />
      </TestWrapper>
    );

    await waitFor(async () => {
      const nickname = await screen.findByText('ImageUser');
      expect(nickname).toBeInTheDocument();
    });

    expect(screen.getByText('AUTHOR')).toBeInTheDocument();
  });
});
