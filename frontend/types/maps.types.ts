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
  objectType: ObjectType;
  coordinates: Record<string, unknown>; // JSON field
  label: string;
  description: string;
  wikiEntryId: number | null;
  styleJson: Record<string, unknown> | null;
  createdAt: string;
}

// =============================================================================
// Map Layer
// =============================================================================

export interface MapLayer {
  id: number;
  name: string;
  layerType: LayerType;
  zIndex: number;
  isVisible: boolean;
  styleJson: Record<string, unknown> | null;
  objects: MapObject[];
  createdAt: string;
}

// =============================================================================
// Map Snapshot
// =============================================================================

export interface MapSnapshot {
  id: number;
  validFromChapter: number;
  baseImageUrl: string;
  layers: MapLayer[];
  createdAt: string;
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
  sourceMapId: number | null;
  snapshots: MapSnapshot[];
  snapshot: MapSnapshot | null;
  createdAt: string;
  updatedAt: string;
}

export interface MapSummary {
  id: number;
  name: string;
  description: string;
  width: number;
  height: number;
  createdAt: string;
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
  validFromChapter: number;
  baseImageUrl?: string;
}

export interface MapLayerCreateRequest {
  name: string;
  layerType?: LayerType;
  zIndex?: number;
  isVisible?: boolean;
  styleJson?: Record<string, unknown> | null;
}

export interface MapObjectCreateRequest {
  objectType: ObjectType;
  coordinates: Record<string, unknown>;
  label?: string;
  description?: string;
  wikiEntryId?: number | null;
  styleJson?: Record<string, unknown> | null;
}

export interface MapListParams extends PageParams {
  branchId: number;
  search?: string;
}
