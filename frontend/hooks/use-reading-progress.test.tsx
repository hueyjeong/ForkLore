import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useReadingProgress } from './use-reading-progress';
import { recordReadingProgress } from '@/lib/api/chapters.api';

vi.mock('@/lib/api/chapters.api');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      mutations: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useReadingProgress', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return expected shape', () => {
    const { result } = renderHook(() => useReadingProgress(), {
      wrapper: createWrapper(),
    });

    expect(result.current).toEqual({
      currentChapterNumber: null,
      recordProgress: expect.any(Function),
      isLoading: false,
      error: null,
    });
  });

  it('should call API with correct params when recordProgress is called', async () => {
    const mockResponse = {
      id: 1,
      user: 1,
      chapter: 42,
      progress: 50,
      last_read_at: '2025-01-21T00:00:00Z',
    };
    vi.mocked(recordReadingProgress).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useReadingProgress(), {
      wrapper: createWrapper(),
    });

    await result.current.recordProgress(42, 50);

    expect(recordReadingProgress).toHaveBeenCalledWith(42, 50);
  });

  it('should set isLoading to true during mutation', async () => {
    let resolvePromise: (value: unknown) => void;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    const mockResponse = {
      id: 1,
      user: 1,
      chapter: 42,
      progress: 50,
      last_read_at: '2025-01-21T00:00:00Z',
    };
    vi.mocked(recordReadingProgress).mockReturnValue(pendingPromise as never);

    const { result } = renderHook(() => useReadingProgress(), {
      wrapper: createWrapper(),
    });

    const mutationPromise = result.current.recordProgress(42, 50);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(true);
    });

    resolvePromise!(mockResponse);
    await mutationPromise;
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('should handle errors correctly', async () => {
    const mockError = new Error('Failed to record progress');
    vi.mocked(recordReadingProgress).mockRejectedValue(mockError);

    const { result } = renderHook(() => useReadingProgress(), {
      wrapper: createWrapper(),
    });

    await expect(result.current.recordProgress(42, 50)).rejects.toThrow(
      'Failed to record progress'
    );

    await waitFor(() => {
      expect(result.current.error).toBe(mockError);
    });
  });
});
