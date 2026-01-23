/**
 * Subscription Type Definitions
 * Based on backend/apps/interactions/serializers.py and models.py
 */

import type { ApiResponse } from './common'

// =============================================================================
// Enums (from backend models)
// =============================================================================

export enum PlanType {
  BASIC = 'BASIC',
  PREMIUM = 'PREMIUM',
}

export enum SubscriptionStatus {
  ACTIVE = 'ACTIVE',
  CANCELLED = 'CANCELLED',
  EXPIRED = 'EXPIRED',
}

// =============================================================================
// Subscription Types
// =============================================================================

export interface SubscriptionCreate {
  planType?: PlanType
  days?: number
  paymentId?: string
}

export interface Subscription {
  id: number
  planType: PlanType
  status: SubscriptionStatus
  startedAt: string
  expiresAt: string
  cancelledAt: string | null
  autoRenew: boolean
  createdAt: string
}

export interface SubscriptionStatusResponse {
  id: number
  isActive: boolean
  planType: string
  status: string
  startedAt: string
  expiresAt: string
  cancelledAt: string | null
  autoRenew: boolean
}

// =============================================================================
// Purchase Types
// =============================================================================

export interface Purchase {
  id: number
  chapter: {
    id: number
    title: string
    chapterNumber: number
  }
  pricePaid: number
  createdAt: string
}

export interface PurchaseDetail {
  id: number
  chapterId: number
  chapterTitle: string
  chapterNumber: number
  pricePaid: number
  createdAt: string
}
