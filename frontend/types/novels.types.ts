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
  cover_image_url: string;
  genre: Genre;
  age_rating: AgeRating;
  status: NovelStatus;
  is_exclusive: boolean;
  is_premium: boolean;
  allow_branching: boolean;
  total_view_count: number;
  total_like_count: number;
  // TODO: Backend must always return average_rating (never omit).
  // Keep as required field; frontend uses ?? 0 as fallback for null.
  average_rating: number | null;
  total_chapter_count: number;
  branch_count: number;
  linked_branch_count: number;
  author: Author;
  created_at: string;
  updated_at: string;
}

export interface NovelSummary {
  id: number;
  title: string;
  cover_image_url: string;
  genre: Genre;
  age_rating: AgeRating;
  status: NovelStatus;
  is_exclusive: boolean;
  is_premium: boolean;
  total_view_count: number;
  total_like_count: number;
  branch_count: number;
  author: Author;
  created_at: string;
}

// =============================================================================
// Novel Request/Response Types
// =============================================================================

export interface NovelCreateRequest {
  title: string;
  description?: string;
  cover_image_url?: string;
  genre: Genre;
  age_rating?: AgeRating;
  status?: NovelStatus;
  allow_branching?: boolean;
}

export interface NovelUpdateRequest {
  title?: string;
  description?: string;
  cover_image_url?: string;
  genre?: Genre;
  age_rating?: AgeRating;
  status?: NovelStatus;
  allow_branching?: boolean;
}

export interface NovelListParams extends PageParams {
  genre?: Genre;
  age_rating?: AgeRating;
  status?: NovelStatus;
  is_exclusive?: boolean;
  is_premium?: boolean;
  author_id?: number;
  search?: string;
}
