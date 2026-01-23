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
  profileImage: string | null
}

export interface ChapterBrief {
  id: number
  title: string
  chapterNumber: number
}

// =============================================================================
// Comment Types
// =============================================================================

export interface CommentCreate {
  content: string
  isSpoiler?: boolean
  parentId?: number | null
  paragraphIndex?: number | null
  selectionStart?: number | null
  selectionEnd?: number | null
  quotedText?: string
}

export interface CommentUpdate {
  content?: string
  isSpoiler?: boolean
}

export interface Comment {
  id: number
  user: UserBrief
  content: string
  isSpoiler: boolean
  isPinned: boolean
  likeCount: number
  paragraphIndex: number | null
  selectionStart: number | null
  selectionEnd: number | null
  quotedText: string
  parentId: number | null
  replyCount: number
  createdAt: string
  updatedAt: string
}

// =============================================================================
// Like Types
// =============================================================================

export interface LikeToggleResponse {
  liked: boolean
  likeCount: number | null
}

// =============================================================================
// Bookmark Types
// =============================================================================

export interface BookmarkCreate {
  scrollPosition?: number
  note?: string
}

export interface Bookmark {
  id: number
  chapter: ChapterBrief
  scrollPosition: number
  note: string
  createdAt: string
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
  isCompleted: boolean
  readAt: string
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
  targetType: ReportTargetType
  targetId: number
  reason: ReportReason
  description?: string
}

export interface Report {
  id: number
  reporter: UserBrief
  targetType: string
  targetId: number
  reason: ReportReason
  description: string
  status: ReportStatus
  createdAt: string
}

export interface ReportAdmin {
  id: number
  reporter: UserBrief
  targetType: string
  targetId: number
  reason: ReportReason
  description: string
  status: ReportStatus
  resolver: UserBrief | null
  resolvedAt: string | null
  resolutionNote: string
  createdAt: string
  updatedAt: string
}

export interface ReportAction {
  action: 'resolve' | 'reject'
  resolutionNote?: string
}

// =============================================================================
// Purchase Types
// =============================================================================

export interface Purchase {
  id: number
  chapter: ChapterBrief
  cost: number
  purchasedAt: string
}
