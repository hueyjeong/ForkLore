import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { toast } from 'sonner';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MyLibrary } from './my-library';
import type { Purchase } from '@/types/interactions.types';

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

import { apiClient } from '@/lib/api-client';

const mockPurchases: Purchase[] = [
  {
    id: 1,
    chapter: {
      id: 1,
      title: 'The Beginning',
      chapterNumber: 1,
    },
    cost: 100,
    purchasedAt: '2024-01-15T10:30:00Z',
  },
  {
    id: 2,
    chapter: {
      id: 2,
      title: 'The Journey',
      chapterNumber: 2,
    },
    cost: 150,
    purchasedAt: '2024-01-16T14:45:00Z',
  },
];

const createMockResponse = (results: Purchase[]) => ({
  data: {
    data: {
      results,
      total: results.length,
      page: 1,
      size: 50,
      hasNext: false,
    },
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

describe('MyLibrary - useQuery Refactoring', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiClient.get as any).mockResolvedValue(createMockResponse(mockPurchases));
  });

  it('should fetch purchases using useQuery', async () => {
    render(
      <TestWrapper>
        <MyLibrary />
      </TestWrapper>
    );

    await waitFor(async () => {
      const title = await screen.findByText('The Beginning');
      expect(title).toBeInTheDocument();
    });

    expect(apiClient.get).toHaveBeenCalledWith('/purchases/', { params: { page: 1, size: 50 } });
    expect(apiClient.get).toHaveBeenCalledTimes(1);

    expect(screen.getByText('The Beginning')).toBeInTheDocument();
    expect(screen.getByText('The Journey')).toBeInTheDocument();
    expect(screen.getByText('2 Items')).toBeInTheDocument();
  });

  it('should show Loader2 spinner while loading', async () => {
    (apiClient.get as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(createMockResponse(mockPurchases)), 100))
    );

    render(
      <TestWrapper>
        <MyLibrary />
      </TestWrapper>
    );

    expect(screen.queryByText('The Beginning')).not.toBeInTheDocument();

    const loadingContainer = document.querySelector('.animate-spin');
    expect(loadingContainer).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText('The Beginning')).toBeInTheDocument();
    });
  });

  it('should show empty state when no purchases', async () => {
    (apiClient.get as any).mockResolvedValue(createMockResponse([]));

    render(
      <TestWrapper>
        <MyLibrary />
      </TestWrapper>
    );

    await waitFor(async () => {
      const emptyState = await screen.findByText("You haven't purchased any chapters yet.");
      expect(emptyState).toBeInTheDocument();
    });

    expect(screen.getByText("You haven't purchased any chapters yet.")).toBeInTheDocument();
    expect(screen.getByText('0 Items')).toBeInTheDocument();
  });

  it('should show toast error on API failure', async () => {
    const toastSpy = vi.spyOn(toast, 'error');

    (apiClient.get as any).mockRejectedValue(new Error('API Error'));

    render(
      <TestWrapper>
        <MyLibrary />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(toastSpy).toHaveBeenCalledWith('Failed to load library');
    });
  });

  it('should render chapter details correctly', async () => {
    render(
      <TestWrapper>
        <MyLibrary />
      </TestWrapper>
    );

    await waitFor(async () => {
      const title = await screen.findByText('The Beginning');
      expect(title).toBeInTheDocument();
    });

    expect(screen.getByText('Chapter 1')).toBeInTheDocument();
    expect(screen.getByText('100 C')).toBeInTheDocument();
    expect(screen.getByText('150 C')).toBeInTheDocument();
    expect(screen.getByText(/1\/15\/2024/)).toBeInTheDocument();
    expect(screen.getByText(/1\/16\/2024/)).toBeInTheDocument();
  });

  it('should display correct item count in badge', async () => {
    render(
      <TestWrapper>
        <MyLibrary />
      </TestWrapper>
    );

    await waitFor(async () => {
      const badge = await screen.findByText('2 Items');
      expect(badge).toBeInTheDocument();
    });
  });
});
