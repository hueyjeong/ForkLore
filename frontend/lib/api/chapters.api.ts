import { apiClient } from '@/lib/api-client';
import { ApiResponse, PaginatedResponse } from '@/types/common';
import {
  Chapter,
  ChapterCreateRequest,
  ChapterUpdateRequest,
  ChapterScheduleRequest,
  ChapterListParams,
  ReadingProgress,
} from '@/types/chapters.types';

const BASE_URL = '/chapters';

/**
 * Get list of chapters for a branch
 */
export async function getChapters(
  branchId: number,
  params?: Omit<ChapterListParams, 'branch_id'>
): Promise<PaginatedResponse<Chapter>> {
  const response = await apiClient.get<ApiResponse<PaginatedResponse<Chapter>>>(
    `/branches/${branchId}/chapters`,
    { params }
  );
  return response.data.data;
}

/**
 * Get chapter details
 */
export async function getChapter(id: number): Promise<Chapter> {
  const response = await apiClient.get<ApiResponse<Chapter>>(`${BASE_URL}/${id}`);
  return response.data.data;
}

/**
 * Create a new chapter
 */
export async function createChapter(
  branchId: number,
  data: ChapterCreateRequest
): Promise<Chapter> {
  const response = await apiClient.post<ApiResponse<Chapter>>(
    `/branches/${branchId}/chapters`,
    data
  );
  return response.data.data;
}

/**
 * Update an existing chapter
 */
export async function updateChapter(
  id: number,
  data: ChapterUpdateRequest
): Promise<Chapter> {
  const response = await apiClient.patch<ApiResponse<Chapter>>(
    `${BASE_URL}/${id}`,
    data
  );
  return response.data.data;
}

/**
 * Delete a chapter
 */
export async function deleteChapter(id: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`${BASE_URL}/${id}`);
}

/**
 * Publish a chapter
 */
export async function publishChapter(id: number): Promise<Chapter> {
  const response = await apiClient.post<ApiResponse<Chapter>>(
    `${BASE_URL}/${id}/publish`
  );
  return response.data.data;
}

/**
 * Schedule a chapter for future publication
 */
export async function scheduleChapter(
  id: number,
  data: ChapterScheduleRequest
): Promise<Chapter> {
  const response = await apiClient.post<ApiResponse<Chapter>>(
    `${BASE_URL}/${id}/schedule`,
    data
  );
  return response.data.data;
}

/**
 * Unschedule a chapter (cancel scheduled publication)
 */
export async function unscheduleChapter(id: number): Promise<Chapter> {
  const response = await apiClient.post<ApiResponse<Chapter>>(
    `${BASE_URL}/${id}/unschedule`
  );
  return response.data.data;
}

/**
 * Record reading progress for a chapter
 */
export async function recordReadingProgress(
  chapterId: number,
  progress: number
): Promise<ReadingProgress> {
  const response = await apiClient.post<ApiResponse<ReadingProgress>>(
    `/chapters/${chapterId}/reading-progress`,
    { progress }
  );
  return response.data.data;
}
