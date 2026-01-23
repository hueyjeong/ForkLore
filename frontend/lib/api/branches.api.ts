import { apiClient } from '@/lib/api-client';
import { ApiResponse, PaginatedResponse } from '@/types/common';
import {
  Branch,
  BranchCreateRequest,
  BranchUpdateRequest,
  BranchVisibilityUpdateRequest,
  BranchListParams,
  BranchLinkRequestCreateRequest,
  BranchLinkRequestReviewRequest,
} from '@/types/branches.types';

const BASE_URL = '/branches';

/**
 * Get list of branches for a novel
 */
export async function getBranches(
  novelId: number,
  params?: Omit<BranchListParams, 'novelId'>
): Promise<PaginatedResponse<Branch>> {
  const response = await apiClient.get<ApiResponse<PaginatedResponse<Branch>>>(
    `/novels/${novelId}/branches`,
    { params }
  );
  return response.data.data;
}

/**
 * Get branch details
 */
export async function getBranch(id: number): Promise<Branch> {
  const response = await apiClient.get<ApiResponse<Branch>>(`${BASE_URL}/${id}`);
  return response.data.data;
}

/**
 * Create a new branch
 */
export async function createBranch(
  novelId: number,
  data: BranchCreateRequest
): Promise<Branch> {
  const response = await apiClient.post<ApiResponse<Branch>>(
    `/novels/${novelId}/branches`,
    data
  );
  return response.data.data;
}

/**
 * Update a branch
 */
export async function updateBranch(
  id: number,
  data: BranchUpdateRequest
): Promise<Branch> {
  const response = await apiClient.patch<ApiResponse<Branch>>(
    `${BASE_URL}/${id}`,
    data
  );
  return response.data.data;
}

/**
 * Update branch visibility
 */
export async function updateBranchVisibility(
  id: number,
  data: BranchVisibilityUpdateRequest
): Promise<Branch> {
  const response = await apiClient.patch<ApiResponse<Branch>>(
    `${BASE_URL}/${id}/visibility`,
    data
  );
  return response.data.data;
}

/**
 * Delete a branch
 */
export async function deleteBranch(id: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`${BASE_URL}/${id}`);
}

/**
 * Vote for a branch
 */
export async function voteBranch(id: number): Promise<Branch> {
  const response = await apiClient.post<ApiResponse<Branch>>(`${BASE_URL}/${id}/vote`);
  return response.data.data;
}

/**
 * Remove vote for a branch
 */
export async function unvoteBranch(id: number): Promise<Branch> {
  const response = await apiClient.delete<ApiResponse<Branch>>(`${BASE_URL}/${id}/vote`);
  return response.data.data;
}

/**
 * Create a link request for a branch
 */
export async function createLinkRequest(
  id: number,
  data?: BranchLinkRequestCreateRequest
): Promise<{ id: number; message: string }> {
  const response = await apiClient.post<ApiResponse<{ id: number; message: string }>>(
    `${BASE_URL}/${id}/link-request`,
    data || {}
  );
  return response.data.data;
}
