import { PageParams } from './common';

// =============================================================================
// Enums
// =============================================================================

export enum LayerType {
  BASE = 'BASE',
  OVERLAY = 'OVERLAY',
  MARKER = 'MARKER',
  PATH = 'PATH',
  REGION = 'REGION',
}

export enum ObjectType {
  POINT = 'POINT',
  LINE = 'LINE',
  POLYGON = 'POLYGON',
  CIRCLE = 'CIRCLE',
  ICON = 'ICON',
}

export enum ContributorType {
  USER = 'USER',
  AI = 'AI',
}

// =============================================================================
// Map Object
// =============================================================================

export interface MapObject {
  id: number;
  object_type: ObjectType;
  coordinates: Record<string, unknown>; // JSON field
  label: string;
  description: string;
  wiki_entry_id: number | null;
  style_json: Record<string, unknown> | null;
  created_at: string;
}

// =============================================================================
// Map Layer
// =============================================================================

export interface MapLayer {
  id: number;
  name: string;
  layer_type: LayerType;
  z_index: number;
  is_visible: boolean;
  style_json: Record<string, unknown> | null;
  objects: MapObject[];
  created_at: string;
}

// =============================================================================
// Map Snapshot
// =============================================================================

export interface MapSnapshot {
  id: number;
  valid_from_chapter: number;
  base_image_url: string;
  layers: MapLayer[];
  created_at: string;
}

// =============================================================================
// Map
// =============================================================================

export interface Map {
  id: number;
  name: string;
  description: string;
  width: number;
  height: number;
  source_map_id: number | null;
  snapshots: MapSnapshot[];
  snapshot: MapSnapshot | null;
  created_at: string;
  updated_at: string;
}

export interface MapSummary {
  id: number;
  name: string;
  description: string;
  width: number;
  height: number;
  created_at: string;
}

// =============================================================================
// Map Request/Response Types
// =============================================================================

export interface MapCreateRequest {
  name: string;
  description?: string;
  width: number;
  height: number;
}

export interface MapUpdateRequest {
  name?: string;
  description?: string;
  width?: number;
  height?: number;
}

export interface MapSnapshotCreateRequest {
  valid_from_chapter: number;
  base_image_url?: string;
}

export interface MapLayerCreateRequest {
  name: string;
  layer_type?: LayerType;
  z_index?: number;
  is_visible?: boolean;
  style_json?: Record<string, unknown> | null;
}

export interface MapObjectCreateRequest {
  object_type: ObjectType;
  coordinates: Record<string, unknown>;
  label?: string;
  description?: string;
  wiki_entry_id?: number | null;
  style_json?: Record<string, unknown> | null;
}

export interface MapListParams extends PageParams {
  branch_id: number;
  search?: string;
}
