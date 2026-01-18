import { apiClient } from '@/lib/api-client';
import { ApiResponse, PaginatedResponse, PageParams } from '@/types/common';
import {
  Comment,
  CommentCreate,
  CommentUpdate,
  LikeToggleResponse,
  ReportCreate,
  Report,
} from '@/types/interactions.types';

const BASE_URL = '/chapters';

/**
 * Get list of comments for a chapter
 */
export async function getComments(
  chapterId: number,
  params?: PageParams
): Promise<PaginatedResponse<Comment>> {
  const response = await apiClient.get<ApiResponse<PaginatedResponse<Comment>>>(
    `${BASE_URL}/${chapterId}/comments`,
    { params }
  );
  return response.data.data;
}

/**
 * Create a new comment on a chapter
 */
export async function createComment(
  chapterId: number,
  data: CommentCreate
): Promise<Comment> {
  const response = await apiClient.post<ApiResponse<Comment>>(
    `${BASE_URL}/${chapterId}/comments`,
    data
  );
  return response.data.data;
}

/**
 * Update an existing comment
 */
export async function updateComment(
  commentId: number,
  data: CommentUpdate
): Promise<Comment> {
  const response = await apiClient.patch<ApiResponse<Comment>>(
    `/comments/${commentId}`,
    data
  );
  return response.data.data;
}

/**
 * Delete a comment
 */
export async function deleteComment(commentId: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`/comments/${commentId}`);
}

/**
 * Like a chapter
 */
export async function likeChapter(chapterId: number): Promise<LikeToggleResponse> {
  const response = await apiClient.post<ApiResponse<LikeToggleResponse>>(
    `${BASE_URL}/${chapterId}/like`
  );
  return response.data.data;
}

/**
 * Unlike a chapter
 */
export async function unlikeChapter(chapterId: number): Promise<LikeToggleResponse> {
  const response = await apiClient.delete<ApiResponse<LikeToggleResponse>>(
    `${BASE_URL}/${chapterId}/like`
  );
  return response.data.data;
}

/**
 * Purchase a chapter
 */
export async function purchaseChapter(chapterId: number): Promise<void> {
  await apiClient.post<ApiResponse<void>>(`${BASE_URL}/${chapterId}/purchase`);
}

/**
 * Create a report
 */
export async function createReport(data: ReportCreate): Promise<Report> {
  const response = await apiClient.post<ApiResponse<Report>>('/reports', data);
  return response.data.data;
}
