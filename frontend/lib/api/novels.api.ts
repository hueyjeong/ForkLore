import { apiClient } from '@/lib/api-client';
import { ApiResponse } from '@/types/common';
import {
  Novel,
  NovelCreateRequest,
  NovelUpdateRequest,
  NovelListParams,
} from '@/types/novels.types';

const BASE_URL = '/novels/novels';

interface DjangoPaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface TransformedPaginatedResponse<T> {
  results: T[];
  total: number;
  page: number;
  hasNext: boolean;
}

export async function getNovels(
  params?: NovelListParams
): Promise<TransformedPaginatedResponse<Novel>> {
  const response = await apiClient.get<ApiResponse<DjangoPaginatedResponse<Novel>>>(
    BASE_URL,
    { params }
  );
  const data = response.data.data;
  const page = params?.page || 1;
  const limit = params?.limit || 12;
  return {
    results: data.results,
    total: data.count,
    page,
    hasNext: data.next !== null,
  };
}

/**
 * Get novel details
 */
export async function getNovel(id: number): Promise<Novel> {
  const response = await apiClient.get<ApiResponse<Novel>>(`${BASE_URL}/${id}`);
  return response.data.data;
}

/**
 * Create a new novel
 */
export async function createNovel(data: NovelCreateRequest): Promise<Novel> {
  const response = await apiClient.post<ApiResponse<Novel>>(BASE_URL, data);
  return response.data.data;
}

/**
 * Update an existing novel
 */
export async function updateNovel(
  id: number,
  data: NovelUpdateRequest
): Promise<Novel> {
  const response = await apiClient.patch<ApiResponse<Novel>>(
    `${BASE_URL}/${id}`,
    data
  );
  return response.data.data;
}

/**
 * Delete a novel
 */
export async function deleteNovel(id: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`${BASE_URL}/${id}`);
}
