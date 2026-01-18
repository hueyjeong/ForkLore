/**
 * Interactions Type Definitions
 * Based on backend/apps/interactions/serializers.py and models.py
 */

import type { ApiResponse } from './common'

// =============================================================================
// Enums (from backend models)
// =============================================================================

export enum ReportReason {
  SPAM = 'SPAM',
  ABUSE = 'ABUSE',
  SPOILER = 'SPOILER',
  COPYRIGHT = 'COPYRIGHT',
  OTHER = 'OTHER',
}

export enum ReportStatus {
  PENDING = 'PENDING',
  RESOLVED = 'RESOLVED',
  REJECTED = 'REJECTED',
}

// =============================================================================
// Shared Types
// =============================================================================

export interface UserBrief {
  id: number
  nickname: string
  profile_image: string | null
}

export interface ChapterBrief {
  id: number
  title: string
  chapter_number: number
}

// =============================================================================
// Comment Types
// =============================================================================

export interface CommentCreate {
  content: string
  is_spoiler?: boolean
  parent_id?: number | null
  paragraph_index?: number | null
  selection_start?: number | null
  selection_end?: number | null
  quoted_text?: string
}

export interface CommentUpdate {
  content?: string
  is_spoiler?: boolean
}

export interface Comment {
  id: number
  user: UserBrief
  content: string
  is_spoiler: boolean
  is_pinned: boolean
  like_count: number
  paragraph_index: number | null
  selection_start: number | null
  selection_end: number | null
  quoted_text: string
  parent_id: number | null
  reply_count: number
  created_at: string
  updated_at: string
}

// =============================================================================
// Like Types
// =============================================================================

export interface LikeToggleResponse {
  liked: boolean
  like_count: number | null
}

// =============================================================================
// Bookmark Types
// =============================================================================

export interface BookmarkCreate {
  scroll_position?: number
  note?: string
}

export interface Bookmark {
  id: number
  chapter: ChapterBrief
  scroll_position: number
  note: string
  created_at: string
}

// =============================================================================
// Reading Log Types
// =============================================================================

export interface ReadingProgress {
  progress: number
}

export interface ReadingLog {
  id: number
  chapter: ChapterBrief
  progress: number
  is_completed: boolean
  read_at: string
}

export interface ContinueReading {
  chapter: ChapterBrief | null
  progress: number
}

// =============================================================================
// Report Types
// =============================================================================

export type ReportTargetType = 'comment' | 'chapter' | 'novel' | 'branch'

export interface ReportCreate {
  target_type: ReportTargetType
  target_id: number
  reason: ReportReason
  description?: string
}

export interface Report {
  id: number
  reporter: UserBrief
  target_type: string
  target_id: number
  reason: ReportReason
  description: string
  status: ReportStatus
  created_at: string
}

export interface ReportAdmin {
  id: number
  reporter: UserBrief
  target_type: string
  target_id: number
  reason: ReportReason
  description: string
  status: ReportStatus
  resolver: UserBrief | null
  resolved_at: string | null
  resolution_note: string
  created_at: string
  updated_at: string
}

export interface ReportAction {
  action: 'resolve' | 'reject'
  resolution_note?: string
}
