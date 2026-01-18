import { PageParams } from './common';

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
  display_order: number;
  created_at: string;
}

// =============================================================================
// Wiki Snapshot
// =============================================================================

export interface WikiSnapshot {
  id: number;
  content: string;
  valid_from_chapter: number;
  contributor_type: ContributorType;
  created_at: string;
}

// =============================================================================
// Wiki Entry
// =============================================================================

export interface WikiEntry {
  id: number;
  name: string;
  image_url: string;
  first_appearance: number | null;
  hidden_note: string;
  ai_metadata: Record<string, unknown> | null;
  tags: WikiTagDefinition[];
  snapshots: WikiSnapshot[];
  snapshot: WikiSnapshot | null;
  created_at: string;
  updated_at: string;
}

export interface WikiEntrySummary {
  id: number;
  name: string;
  image_url: string;
  first_appearance: number | null;
  tags: WikiTagDefinition[];
  created_at: string;
}

// =============================================================================
// Wiki Request/Response Types
// =============================================================================

export interface WikiEntryCreateRequest {
  name: string;
  image_url?: string;
  first_appearance?: number | null;
  hidden_note?: string;
  initial_content?: string;
}

export interface WikiEntryUpdateRequest {
  name?: string;
  image_url?: string;
  first_appearance?: number | null;
  hidden_note?: string;
}

export interface WikiTagCreateRequest {
  name: string;
  color?: string;
  icon?: string;
  description?: string;
  display_order?: number;
}

export interface WikiSnapshotCreateRequest {
  content: string;
  valid_from_chapter: number;
}

export interface WikiTagUpdateRequest {
  tag_ids: number[];
}

export interface WikiListParams extends PageParams {
  branch_id: number;
  tag_id?: number;
  search?: string;
  chapter?: number; // For context-aware snapshot retrieval
}
