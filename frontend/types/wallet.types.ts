/**
 * Wallet Type Definitions
 * Based on backend/apps/interactions/serializers.py and models.py
 */

import type { ApiResponse } from './common'

// =============================================================================
// Enums (from backend models)
// =============================================================================

export enum TransactionType {
  CHARGE = 'CHARGE',
  SPEND = 'SPEND',
  REFUND = 'REFUND',
  ADJUSTMENT = 'ADJUSTMENT',
}

// =============================================================================
// Wallet Types
// =============================================================================

export interface WalletCharge {
  amount: number
  description?: string
}

export interface WalletAdjustment {
  amount: number
  description?: string
}

export interface CoinTransaction {
  id: number
  transactionType: TransactionType
  amount: number
  balanceAfter: number
  description: string
  referenceType: string
  referenceId: number | null
  createdAt: string
}

export interface Wallet {
  balance: number
  recentTransactions: CoinTransaction[]
}

export interface WalletBalanceResponse {
  balance: number
  transaction: CoinTransaction
}
