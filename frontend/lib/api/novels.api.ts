import { apiClient } from '@/lib/api-client';
import { ApiResponse, PaginatedResponse } from '@/types/common';
import {
  Novel,
  CreateNovelRequest,
  UpdateNovelRequest,
  NovelListParams,
} from '@/types/novels.types';

const BASE_URL = '/novels';

/**
 * Get list of novels
 */
export async function getNovels(
  params?: NovelListParams
): Promise<PaginatedResponse<Novel>> {
  const response = await apiClient.get<ApiResponse<PaginatedResponse<Novel>>>(
    BASE_URL,
    { params }
  );
  return response.data.data;
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
export async function createNovel(data: CreateNovelRequest): Promise<Novel> {
  const response = await apiClient.post<ApiResponse<Novel>>(BASE_URL, data);
  return response.data.data;
}

/**
 * Update an existing novel
 */
export async function updateNovel(
  id: number,
  data: UpdateNovelRequest
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
