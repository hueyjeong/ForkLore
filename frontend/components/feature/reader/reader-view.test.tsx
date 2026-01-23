import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReaderView } from './reader-view';

const mockPush = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

import { apiClient } from '@/lib/api-client';

const mockChapter = {
  id: 1,
  chapterNumber: 1,
  title: 'The Beginning',
  contentHtml: '<p>This is the story...</p>',
  wordCount: 1000,
  status: 'PUBLISHED',
  accessType: 'FREE',
  price: 0,
  scheduledAt: null,
  publishedAt: '2024-01-01T00:00:00Z',
  viewCount: 100,
  likeCount: 10,
  commentCount: 5,
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
  prevChapter: null,
  nextChapter: {
    id: 2,
    chapterNumber: 2,
    title: 'Chapter 2',
  },
};

const mockChapter2 = {
  ...mockChapter,
  id: 2,
  chapterNumber: 2,
  title: 'Chapter 2',
  nextChapter: null,
  prevChapter: {
    id: 1,
    chapterNumber: 1,
    title: 'The Beginning',
  },
};

const createMockResponse = (chapter: typeof mockChapter) => ({
  data: {
    data: chapter,
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

describe('ReaderView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPush.mockClear();
    (apiClient.get as any).mockResolvedValue(createMockResponse(mockChapter));
  });

  it('should render loading state with Loader2 spinner', async () => {
    (apiClient.get as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(createMockResponse(mockChapter)), 100))
    );

    render(
      <TestWrapper>
        <ReaderView chapterId={1} novelId={1} />
      </TestWrapper>
    );

    expect(screen.queryByText('The Beginning')).not.toBeInTheDocument();

    const loadingContainer = document.querySelector('.animate-spin');
    expect(loadingContainer).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText('The Beginning')).toBeInTheDocument();
    });
  });

  it('should render chapter content after successful fetch', async () => {
    render(
      <TestWrapper>
        <ReaderView chapterId={1} novelId={1} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('The Beginning')).toBeInTheDocument();
    });

    expect(screen.getByText('This is the story...')).toBeInTheDocument();
  });

  it('should show error state when fetch fails', async () => {
    (apiClient.get as any).mockRejectedValue(new Error('Network error'));

    render(
      <TestWrapper>
        <ReaderView chapterId={1} novelId={1} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to load chapter')).toBeInTheDocument();
    });

    const returnButton = screen.getByRole('link', { name: /return to novel/i });
    expect(returnButton).toBeInTheDocument();
    expect(returnButton).toHaveAttribute('href', '/novels/1');
  });

  it('should refetch when chapterId changes', async () => {
    const { rerender } = render(
      <TestWrapper>
        <ReaderView chapterId={1} novelId={1} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('The Beginning')).toBeInTheDocument();
    });

    (apiClient.get as any).mockResolvedValue(createMockResponse(mockChapter2));

    rerender(
      <TestWrapper>
        <ReaderView chapterId={2} novelId={1} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Chapter 2')).toBeInTheDocument();
    });

    expect(apiClient.get).toHaveBeenCalledWith('/chapters/2/');
  });

  it('should not fetch when chapterId is 0', async () => {
    render(
      <TestWrapper>
        <ReaderView chapterId={0} novelId={1} />
      </TestWrapper>
    );

    expect(apiClient.get).not.toHaveBeenCalled();
  });

  it('should show navigation buttons based on chapter data', async () => {
    render(
      <TestWrapper>
        <ReaderView chapterId={1} novelId={1} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('The Beginning')).toBeInTheDocument();
    });

    const nextButton = screen.getByRole('button', { name: /next/i });
    expect(nextButton).not.toBeDisabled();

    const prevButton = screen.getByRole('button', { name: /prev/i });
    expect(prevButton).toBeDisabled();
  });

  it('should use correct queryKey for chapter fetching', async () => {
    render(
      <TestWrapper>
        <ReaderView chapterId={1} novelId={1} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalled();
    });

    expect(apiClient.get).toHaveBeenCalledWith('/chapters/1/');
  });
});
