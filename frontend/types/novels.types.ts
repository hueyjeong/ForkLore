import { PageParams } from './common';

// =============================================================================
// Enums
// =============================================================================

// TODO: Backend sync required - The following 6 genres are frontend-only and missing on the backend:
// LIGHT_NOVEL, BL, GL, TS, SPORTS, ALTERNATIVE_HISTORY
// Update backend Genre enum (apps/novels/models.py) to include these keys,
// or map ALTERNATIVE_HISTORY to existing HISTORY key if intended.
// Ensure serializers and validation accept these values for consistent novel creation/filtering.
export enum Genre {
  FANTASY = 'FANTASY',
  ROMANCE = 'ROMANCE',
  ACTION = 'ACTION',
  THRILLER = 'THRILLER',
  MYSTERY = 'MYSTERY',
  SF = 'SF',
  HISTORY = 'HISTORY',
  MODERN = 'MODERN',
  MARTIAL = 'MARTIAL',
  GAME = 'GAME',
  LIGHT_NOVEL = 'LIGHT_NOVEL',
  BL = 'BL',
  GL = 'GL',
  TS = 'TS',
  SPORTS = 'SPORTS',
  ALTERNATIVE_HISTORY = 'ALTERNATIVE_HISTORY',
}

export enum AgeRating {
  ALL = 'ALL',
  AGE_12 = '12',
  AGE_15 = '15',
  AGE_19 = '19',
}

export enum NovelStatus {
  ONGOING = 'ONGOING',
  COMPLETED = 'COMPLETED',
  HIATUS = 'HIATUS',
}

// =============================================================================
// Author
// =============================================================================

export interface Author {
  id: number;
  nickname: string;
}

// =============================================================================
// Novel
// =============================================================================

export interface Novel {
  id: number;
  title: string;
  description: string;
  coverImageUrl: string;
  genre: Genre;
  ageRating: AgeRating;
  status: NovelStatus;
  isExclusive: boolean;
  isPremium: boolean;
  allowBranching: boolean;
  totalViewCount: number;
  totalLikeCount: number;
  // TODO: Backend must always return averageRating (never omit).
  // Keep as required field; frontend uses ?? 0 as fallback for null.
  averageRating: number | null;
  totalChapterCount: number;
  branchCount: number;
  linkedBranchCount: number;
  author: Author;
  createdAt: string;
  updatedAt: string;
}

export interface NovelSummary {
  id: number;
  title: string;
  coverImageUrl: string;
  genre: Genre;
  ageRating: AgeRating;
  status: NovelStatus;
  isExclusive: boolean;
  isPremium: boolean;
  totalViewCount: number;
  totalLikeCount: number;
  branchCount: number;
  author: Author;
  createdAt: string;
}

// =============================================================================
// Novel Request/Response Types
// =============================================================================

export interface NovelCreateRequest {
  title: string;
  description?: string;
  coverImageUrl?: string;
  genre: Genre;
  ageRating?: AgeRating;
  status?: NovelStatus;
  allowBranching?: boolean;
}

export interface NovelUpdateRequest {
  title?: string;
  description?: string;
  coverImageUrl?: string;
  genre?: Genre;
  ageRating?: AgeRating;
  status?: NovelStatus;
  allowBranching?: boolean;
}

export interface NovelListParams extends PageParams {
  genre?: Genre;
  ageRating?: AgeRating;
  status?: NovelStatus;
  isExclusive?: boolean;
  isPremium?: boolean;
  authorId?: number;
  search?: string;
}
