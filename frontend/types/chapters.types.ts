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
  chapterNumber: number;
  title: string;
}

// =============================================================================
// Chapter
// =============================================================================

export interface Chapter {
  id: number;
  chapterNumber: number;
  title: string;
  contentHtml: string;
  wordCount: number;
  status: ChapterStatus;
  accessType: AccessType;
  price: number;
  scheduledAt: string | null;
  publishedAt: string | null;
  viewCount: number;
  likeCount: number;
  commentCount: number;
  createdAt: string;
  updatedAt: string;
  prevChapter: ChapterNav | null;
  nextChapter: ChapterNav | null;
}

export interface ChapterSummary {
  id: number;
  chapterNumber: number;
  title: string;
  wordCount: number;
  status: ChapterStatus;
  accessType: AccessType;
  price: number;
  scheduledAt: string | null;
  publishedAt: string | null;
  viewCount: number;
  likeCount: number;
  commentCount: number;
  createdAt: string;
}

// =============================================================================
// Chapter Request/Response Types
// =============================================================================

export interface ChapterCreateRequest {
  title: string;
  content: string;
  accessType?: AccessType;
  price?: number;
}

export interface ChapterUpdateRequest {
  title?: string;
  content?: string;
  accessType?: AccessType;
  price?: number;
}

export interface ChapterScheduleRequest {
  scheduledAt: string; // ISO datetime string
}

export interface ChapterListParams extends PageParams {
  branchId: number;
  status?: ChapterStatus;
  accessType?: AccessType;
  chapterNumber?: number;
}
