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
  plan_type?: PlanType
  days?: number
  payment_id?: string
}

export interface Subscription {
  id: number
  plan_type: PlanType
  status: SubscriptionStatus
  started_at: string
  expires_at: string
  cancelled_at: string | null
  auto_renew: boolean
  created_at: string
}

export interface SubscriptionStatusResponse {
  id: number
  is_active: boolean
  plan_type: string
  status: string
  started_at: string
  expires_at: string
  cancelled_at: string | null
  auto_renew: boolean
}

// =============================================================================
// Purchase Types
// =============================================================================

export interface Purchase {
  id: number
  chapter: {
    id: number
    title: string
    chapter_number: number
  }
  price_paid: number
  created_at: string
}

export interface PurchaseDetail {
  id: number
  chapter_id: number
  chapter_title: string
  chapter_number: number
  price_paid: number
  created_at: string
}
