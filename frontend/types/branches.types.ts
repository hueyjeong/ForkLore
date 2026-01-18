import { Author } from './novels.types';
import { PageParams } from './common';

// =============================================================================
// Enums
// =============================================================================

export enum BranchType {
  MAIN = 'MAIN',
  SIDE_STORY = 'SIDE_STORY',
  FAN_FIC = 'FAN_FIC',
  IF_STORY = 'IF_STORY',
}

export enum BranchVisibility {
  PRIVATE = 'PRIVATE',
  PUBLIC = 'PUBLIC',
  LINKED = 'LINKED',
}

export enum CanonStatus {
  NON_CANON = 'NON_CANON',
  CANDIDATE = 'CANDIDATE',
  MERGED = 'MERGED',
}

export enum LinkRequestStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
}

// =============================================================================
// Branch
// =============================================================================

export interface Branch {
  id: number;
  novel_id: number;
  name: string;
  description: string;
  cover_image_url: string;
  is_main: boolean;
  branch_type: BranchType;
  visibility: BranchVisibility;
  canon_status: CanonStatus;
  parent_branch_id: number | null;
  fork_point_chapter: number | null;
  vote_count: number;
  vote_threshold: number;
  view_count: number;
  chapter_count: number;
  author: Author;
  created_at: string;
  updated_at: string;
}

export interface BranchSummary {
  id: number;
  name: string;
  cover_image_url: string;
  is_main: boolean;
  branch_type: BranchType;
  visibility: BranchVisibility;
  vote_count: number;
  view_count: number;
  chapter_count: number;
  author: Author;
  created_at: string;
}

// =============================================================================
// Branch Link Request
// =============================================================================

export interface BranchLinkRequest {
  id: number;
  branch_id: number;
  status: LinkRequestStatus;
  request_message: string;
  reviewer_id: number | null;
  review_comment: string;
  reviewed_at: string | null;
  created_at: string;
}

// =============================================================================
// Branch Request/Response Types
// =============================================================================

export interface BranchCreateRequest {
  name: string;
  description?: string;
  cover_image_url?: string;
  branch_type?: BranchType;
  fork_point_chapter?: number | null;
}

export interface BranchUpdateRequest {
  name?: string;
  description?: string;
  cover_image_url?: string;
}

export interface BranchVisibilityUpdateRequest {
  visibility: BranchVisibility;
}

export interface BranchListParams extends PageParams {
  novel_id: number;
  branch_type?: BranchType;
  visibility?: BranchVisibility;
  is_main?: boolean;
  author_id?: number;
  search?: string;
}

export interface BranchLinkRequestCreateRequest {
  request_message?: string;
}

export interface BranchLinkRequestReviewRequest {
  status: LinkRequestStatus.APPROVED | LinkRequestStatus.REJECTED;
  review_comment?: string;
}

export interface BranchLinkRequestListParams extends PageParams {
  branch_id: number;
  status?: LinkRequestStatus;
}
