/**
 * AI Type Definitions
 * Based on backend/apps/ai/serializers.py and interactions/serializers.py
 */

import type { ApiResponse } from './common'

// =============================================================================
// Enums (from backend models)
// =============================================================================

export enum AIActionType {
  WIKI_SUGGEST = 'WIKI_SUGGEST',
  CONSISTENCY_CHECK = 'CONSISTENCY_CHECK',
  ASK = 'ASK',
}

// =============================================================================
// Wiki Suggestion Types
// =============================================================================

export interface WikiSuggestionRequest {
  text: string
}

export interface WikiSuggestionItem {
  name: string
  description: string
}

export interface WikiSuggestionResponse {
  data: WikiSuggestionItem[]
}

// =============================================================================
// Consistency Check Types
// =============================================================================

export interface ConsistencyCheckRequest {
  chapterId: number
}

export interface ConsistencyCheckResponse {
  consistent: boolean
  issues: string[]
}

// =============================================================================
// Ask (RAG) Types
// =============================================================================

export interface AskRequest {
  question: string
}

export interface AskResponse {
  answer: string
}

// =============================================================================
// Chunk Task Types
// =============================================================================

export interface ChunkTaskRequest {
  chapterId?: number
}

export interface ChunkTaskResponse {
  taskId: string
  status: string
}

// =============================================================================
// AI Usage Tracking Types
// =============================================================================

export interface AIUsageCheckLimit {
  actionType: AIActionType
  enforce?: boolean
}

export interface AIUsageCheckLimitResponse {
  allowed: boolean
  remaining: number
  dailyLimit: number
  tier: string
}

export interface AIUsageRecord {
  actionType: AIActionType
  tokenCount?: number
}

export interface AIUsageRecordResponse {
  used: number
  remaining: number
  dailyLimit: number
}

export interface AIUsageByAction {
  used: number
  remaining: number
}

export interface AIUsageStatus {
  tier: string
  dailyLimit: number
  usageByAction: Record<string, AIUsageByAction>
  date: string
}
