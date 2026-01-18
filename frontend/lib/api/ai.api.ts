import { apiClient } from '@/lib/api-client';
import { ApiResponse } from '@/types/common';
import {
  WikiSuggestionRequest,
  WikiSuggestionResponse,
  ConsistencyCheckRequest,
  ConsistencyCheckResponse,
  AskRequest,
  AskResponse,
  ChunkTaskRequest,
  ChunkTaskResponse,
} from '@/types/ai.types';

const BASE_URL = '/branches';

/**
 * Get wiki suggestions for a branch
 */
export async function getWikiSuggestions(
  branchId: number,
  data: WikiSuggestionRequest
): Promise<WikiSuggestionResponse> {
  const response = await apiClient.post<ApiResponse<WikiSuggestionResponse>>(
    `${BASE_URL}/${branchId}/ai/wiki-suggestions`,
    data
  );
  return response.data.data;
}

/**
 * Check consistency of a branch
 */
export async function checkConsistency(
  branchId: number,
  data: ConsistencyCheckRequest
): Promise<ConsistencyCheckResponse> {
  const response = await apiClient.post<ApiResponse<ConsistencyCheckResponse>>(
    `${BASE_URL}/${branchId}/ai/consistency-check`,
    data
  );
  return response.data.data;
}

/**
 * Ask a question about a branch
 */
export async function askBranch(
  branchId: number,
  data: AskRequest
): Promise<AskResponse> {
  const response = await apiClient.post<ApiResponse<AskResponse>>(
    `${BASE_URL}/${branchId}/ai/ask`,
    data
  );
  return response.data.data;
}

/**
 * Create chunks for a branch
 */
export async function createChunks(
  branchId: number,
  data: ChunkTaskRequest
): Promise<ChunkTaskResponse> {
  const response = await apiClient.post<ApiResponse<ChunkTaskResponse>>(
    `${BASE_URL}/${branchId}/ai/create-chunks`,
    data
  );
  return response.data.data;
}
