import { apiClient } from '@/lib/api-client';
import { ApiResponse, PaginatedResponse } from '@/types/common';
import {
  WikiEntry,
  WikiSnapshot,
  WikiTagDefinition,
  WikiEntryCreateRequest,
  WikiEntryUpdateRequest,
  WikiListParams,
} from '@/types/wiki.types';

const BASE_URL = '/wikis';

/**
 * Get list of wiki entries for a branch
 */
export async function getWikis(
  branchId: number,
  params?: Omit<WikiListParams, 'branchId'>
): Promise<PaginatedResponse<WikiEntry>> {
  const response = await apiClient.get<ApiResponse<PaginatedResponse<WikiEntry>>>(
    `/branches/${branchId}/wikis`,
    { params }
  );
  return response.data.data;
}

/**
 * Get list of wiki tags for a branch
 */
export async function getWikiTags(branchId: number): Promise<WikiTagDefinition[]> {
  const response = await apiClient.get<ApiResponse<WikiTagDefinition[]>>(
    `/branches/${branchId}/wiki-tags`
  );
  return response.data.data;
}

/**
 * Get wiki entry details
 * @param id - Wiki entry ID
 * @param chapterId - Optional chapter ID for spoiler-aware retrieval
 */
export async function getWiki(
  id: number,
  chapterId?: number
): Promise<WikiEntry> {
  const response = await apiClient.get<ApiResponse<WikiEntry>>(`${BASE_URL}/${id}`, {
    params: chapterId ? { chapter: chapterId } : undefined,
  });
  return response.data.data;
}

/**
 * Create a new wiki entry
 */
export async function createWiki(
  branchId: number,
  data: WikiEntryCreateRequest
): Promise<WikiEntry> {
  const response = await apiClient.post<ApiResponse<WikiEntry>>(
    `/branches/${branchId}/wikis`,
    data
  );
  return response.data.data;
}

/**
 * Update an existing wiki entry
 */
export async function updateWiki(id: number, data: WikiEntryUpdateRequest): Promise<WikiEntry> {
  const response = await apiClient.patch<ApiResponse<WikiEntry>>(`${BASE_URL}/${id}`, data);
  return response.data.data;
}

/**
 * Delete a wiki entry
 */
export async function deleteWiki(id: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`${BASE_URL}/${id}`);
}

/**
 * Get snapshots for a wiki entry
 */
export async function getWikiSnapshots(wikiId: number): Promise<WikiSnapshot[]> {
  const response = await apiClient.get<ApiResponse<WikiSnapshot[]>>(
    `${BASE_URL}/${wikiId}/snapshots`
  );
  return response.data.data;
}

/**
 * Create a snapshot for a wiki entry at a specific chapter
 */
export async function createWikiSnapshot(
  wikiId: number,
  chapterId: number
): Promise<WikiSnapshot> {
  const response = await apiClient.post<ApiResponse<WikiSnapshot>>(
    `${BASE_URL}/${wikiId}/snapshots`,
    { chapterId }
  );
  return response.data.data;
}
