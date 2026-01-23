import { PageParams, JsonValue } from './common';

// =============================================================================
// Enums
// =============================================================================

export enum ContributorType {
  USER = 'USER',
  AI = 'AI',
}

// =============================================================================
// Wiki Tag Definition
// =============================================================================

export interface WikiTagDefinition {
  id: number;
  name: string;
  color: string;
  icon: string;
  description: string;
  displayOrder: number;
  createdAt: string;
}

// =============================================================================
// Wiki Snapshot
// =============================================================================

export interface WikiSnapshot {
  id: number;
  content: string;
  validFromChapter: number;
  contributorType: ContributorType;
  createdAt: string;
}

// =============================================================================
// Wiki Entry
// =============================================================================

export interface WikiEntry {
  id: number;
  name: string;
  imageUrl: string;
  firstAppearance: number | null;
  hiddenNote: string;
  aiMetadata: Record<string, JsonValue> | null;
  tags: WikiTagDefinition[];
  snapshots: WikiSnapshot[];
  snapshot: WikiSnapshot | null;
  createdAt: string;
  updatedAt: string;
}

export interface WikiEntrySummary {
  id: number;
  name: string;
  imageUrl: string;
  firstAppearance: number | null;
  tags: WikiTagDefinition[];
  createdAt: string;
}

// =============================================================================
// Wiki Request/Response Types
// =============================================================================

export interface WikiEntryCreateRequest {
  name: string;
  imageUrl?: string;
  firstAppearance?: number | null;
  hiddenNote?: string;
  initialContent?: string;
}

export interface WikiEntryUpdateRequest {
  name?: string;
  imageUrl?: string;
  firstAppearance?: number | null;
  hiddenNote?: string;
}

export interface WikiTagCreateRequest {
  name: string;
  color?: string;
  icon?: string;
  description?: string;
  displayOrder?: number;
}

export interface WikiSnapshotCreateRequest {
  content: string;
  validFromChapter: number;
}

export interface WikiTagUpdateRequest {
  tagIds: number[];
}

export interface WikiListParams extends PageParams {
  branchId: number;
  tagId?: number;
  search?: string;
  chapter?: number; // For context-aware snapshot retrieval
}
