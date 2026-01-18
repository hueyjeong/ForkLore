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
  chapter_id: number
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
  chapter_id?: number
}

export interface ChunkTaskResponse {
  task_id: string
  status: string
}

// =============================================================================
// AI Usage Tracking Types
// =============================================================================

export interface AIUsageCheckLimit {
  action_type: AIActionType
  enforce?: boolean
}

export interface AIUsageCheckLimitResponse {
  allowed: boolean
  remaining: number
  daily_limit: number
  tier: string
}

export interface AIUsageRecord {
  action_type: AIActionType
  token_count?: number
}

export interface AIUsageRecordResponse {
  used: number
  remaining: number
  daily_limit: number
}

export interface AIUsageByAction {
  used: number
  remaining: number
}

export interface AIUsageStatus {
  tier: string
  daily_limit: number
  usage_by_action: Record<string, AIUsageByAction>
  date: string
}
