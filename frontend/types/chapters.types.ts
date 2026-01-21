import { PageParams } from './common';

// =============================================================================
// Enums
// =============================================================================

export enum ChapterStatus {
  DRAFT = 'DRAFT',
  SCHEDULED = 'SCHEDULED',
  PUBLISHED = 'PUBLISHED',
}

export enum AccessType {
  FREE = 'FREE',
  SUBSCRIPTION = 'SUBSCRIPTION',
}

// =============================================================================
// Chapter Navigation
// =============================================================================

export interface ChapterNav {
  id: number;
  chapter_number: number;
  title: string;
}

// =============================================================================
// Chapter
// =============================================================================

export interface Chapter {
  id: number;
  chapter_number: number;
  title: string;
  content_html: string;
  word_count: number;
  status: ChapterStatus;
  access_type: AccessType;
  price: number;
  scheduled_at: string | null;
  published_at: string | null;
  view_count: number;
  like_count: number;
  comment_count: number;
  created_at: string;
  updated_at: string;
  prev_chapter: ChapterNav | null;
  next_chapter: ChapterNav | null;
}

export interface ChapterSummary {
  id: number;
  chapter_number: number;
  title: string;
  word_count: number;
  status: ChapterStatus;
  access_type: AccessType;
  price: number;
  scheduled_at: string | null;
  published_at: string | null;
  view_count: number;
  like_count: number;
  comment_count: number;
  created_at: string;
}

// =============================================================================
// Chapter Request/Response Types
// =============================================================================

export interface ChapterCreateRequest {
  title: string;
  content: string;
  access_type?: AccessType;
  price?: number;
}

export interface ChapterUpdateRequest {
  title?: string;
  content?: string;
  access_type?: AccessType;
  price?: number;
}

export interface ChapterScheduleRequest {
  scheduled_at: string; // ISO datetime string
}

export interface ChapterListParams extends PageParams {
  branch_id: number;
  status?: ChapterStatus;
  access_type?: AccessType;
  chapter_number?: number;
}

// =============================================================================
// Reading Progress
// =============================================================================

export interface ReadingProgress {
  id: number;
  user: number;
  chapter: number;
  progress: number;
  last_read_at: string;
}
