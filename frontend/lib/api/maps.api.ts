import { apiClient } from '@/lib/api-client';
import { ApiResponse, PaginatedResponse } from '@/types/common';
import {
  Map,
  MapSnapshot,
  MapLayer,
  MapObject,
  MapCreateRequest,
  MapUpdateRequest,
  MapSnapshotCreateRequest,
  MapLayerCreateRequest,
  MapObjectCreateRequest,
  MapListParams,
} from '@/types/maps.types';

const BASE_URL = '/maps';

/**
 * Get list of maps for a branch
 */
export async function getMaps(
  branchId: number,
  params?: Omit<MapListParams, 'branch_id'>
): Promise<PaginatedResponse<Map>> {
  const response = await apiClient.get<ApiResponse<PaginatedResponse<Map>>>(
    `/branches/${branchId}/maps`,
    { params }
  );
  return response.data.data;
}

/**
 * Get map details
 * @param id - Map ID
 * @param chapterId - Optional chapter ID for spoiler-aware retrieval
 */
export async function getMap(id: number, chapterId?: number): Promise<Map> {
  const response = await apiClient.get<ApiResponse<Map>>(`${BASE_URL}/${id}`, {
    params: chapterId ? { chapter: chapterId } : undefined,
  });
  return response.data.data;
}

/**
 * Create a new map
 */
export async function createMap(
  branchId: number,
  data: MapCreateRequest
): Promise<Map> {
  const response = await apiClient.post<ApiResponse<Map>>(
    `/branches/${branchId}/maps`,
    data
  );
  return response.data.data;
}

/**
 * Update an existing map
 */
export async function updateMap(id: number, data: MapUpdateRequest): Promise<Map> {
  const response = await apiClient.patch<ApiResponse<Map>>(`${BASE_URL}/${id}`, data);
  return response.data.data;
}

/**
 * Delete a map
 */
export async function deleteMap(id: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`${BASE_URL}/${id}`);
}

/**
 * Get snapshots for a map
 */
export async function getMapSnapshots(mapId: number): Promise<MapSnapshot[]> {
  const response = await apiClient.get<ApiResponse<MapSnapshot[]>>(
    `${BASE_URL}/${mapId}/snapshots`
  );
  return response.data.data;
}

/**
 * Create a snapshot for a map at a specific chapter
 */
export async function createMapSnapshot(
  mapId: number,
  data: MapSnapshotCreateRequest
): Promise<MapSnapshot> {
  const response = await apiClient.post<ApiResponse<MapSnapshot>>(
    `${BASE_URL}/${mapId}/snapshots`,
    data
  );
  return response.data.data;
}

/**
 * Delete a map snapshot
 */
export async function deleteMapSnapshot(snapshotId: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`/snapshots/${snapshotId}`);
}

/**
 * Get layers for a map snapshot
 */
export async function getMapLayers(snapshotId: number): Promise<MapLayer[]> {
  const response = await apiClient.get<ApiResponse<MapLayer[]>>(
    `/snapshots/${snapshotId}/layers`
  );
  return response.data.data;
}

/**
 * Create a new layer in a map snapshot
 */
export async function createMapLayer(
  snapshotId: number,
  data: MapLayerCreateRequest
): Promise<MapLayer> {
  const response = await apiClient.post<ApiResponse<MapLayer>>(
    `/snapshots/${snapshotId}/layers`,
    data
  );
  return response.data.data;
}

/**
 * Update an existing map layer
 */
export async function updateMapLayer(
  id: number,
  data: Partial<MapLayerCreateRequest>
): Promise<MapLayer> {
  const response = await apiClient.patch<ApiResponse<MapLayer>>(`/layers/${id}`, data);
  return response.data.data;
}

/**
 * Delete a map layer
 */
export async function deleteMapLayer(id: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`/layers/${id}`);
}

/**
 * Get objects for a map layer
 */
export async function getMapObjects(layerId: number): Promise<MapObject[]> {
  const response = await apiClient.get<ApiResponse<MapObject[]>>(
    `/layers/${layerId}/objects`
  );
  return response.data.data;
}

/**
 * Create a new object in a map layer
 */
export async function createMapObject(
  layerId: number,
  data: MapObjectCreateRequest
): Promise<MapObject> {
  const response = await apiClient.post<ApiResponse<MapObject>>(
    `/layers/${layerId}/objects`,
    data
  );
  return response.data.data;
}

/**
 * Update an existing map object
 */
export async function updateMapObject(
  id: number,
  data: Partial<MapObjectCreateRequest>
): Promise<MapObject> {
  const response = await apiClient.patch<ApiResponse<MapObject>>(`/objects/${id}`, data);
  return response.data.data;
}

/**
 * Delete a map object
 */
export async function deleteMapObject(id: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`/objects/${id}`);
}
