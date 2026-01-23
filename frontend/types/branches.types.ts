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
  novelId: number;
  name: string;
  description: string;
  coverImageUrl: string;
  isMain: boolean;
  branchType: BranchType;
  visibility: BranchVisibility;
  canonStatus: CanonStatus;
  parentBranchId: number | null;
  forkPointChapter: number | null;
  voteCount: number;
  voteThreshold: number;
  viewCount: number;
  chapterCount: number;
  author: Author;
  createdAt: string;
  updatedAt: string;
}

export interface BranchSummary {
  id: number;
  name: string;
  coverImageUrl: string;
  isMain: boolean;
  branchType: BranchType;
  visibility: BranchVisibility;
  voteCount: number;
  viewCount: number;
  chapterCount: number;
  author: Author;
  createdAt: string;
}

// =============================================================================
// Branch Link Request
// =============================================================================

export interface BranchLinkRequest {
  id: number;
  branchId: number;
  status: LinkRequestStatus;
  requestMessage: string;
  reviewerId: number | null;
  reviewComment: string;
  reviewedAt: string | null;
  createdAt: string;
}

// =============================================================================
// Branch Request/Response Types
// =============================================================================

export interface BranchCreateRequest {
  name: string;
  description?: string;
  coverImageUrl?: string;
  branchType?: BranchType;
  forkPointChapter?: number | null;
}

export interface BranchUpdateRequest {
  name?: string;
  description?: string;
  coverImageUrl?: string;
}

export interface BranchVisibilityUpdateRequest {
  visibility: BranchVisibility;
}

export interface BranchListParams extends PageParams {
  novelId: number;
  branchType?: BranchType;
  visibility?: BranchVisibility;
  isMain?: boolean;
  authorId?: number;
  search?: string;
}

export interface BranchLinkRequestCreateRequest {
  requestMessage?: string;
}

export interface BranchLinkRequestReviewRequest {
  status: LinkRequestStatus.APPROVED | LinkRequestStatus.REJECTED;
  reviewComment?: string;
}

export interface BranchLinkRequestListParams extends PageParams {
  branchId: number;
  status?: LinkRequestStatus;
}
