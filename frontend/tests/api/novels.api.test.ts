import { describe, it, expect, vi } from 'vitest';
import { getNovels, getNovel } from '@/lib/api/novels.api';
import { apiClient } from '@/lib/api-client';

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('Novels API', () => {
  it('getNovels should call apiClient.get with correct params', async () => {
    const mockResponse = { data: { data: { results: [], total: 0 } } };
    vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

    await getNovels({ page: 1, limit: 10 });

    expect(apiClient.get).toHaveBeenCalledWith('/novels/', { params: { page: 1, limit: 10 } });
  });

  it('getNovel should call apiClient.get with correct url', async () => {
    const mockResponse = { data: { data: { id: 1, title: 'Test Novel' } } };
    vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

    await getNovel(1);

    expect(apiClient.get).toHaveBeenCalledWith('/novels/1/');
  });
});
