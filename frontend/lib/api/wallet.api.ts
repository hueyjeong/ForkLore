import { apiClient } from '@/lib/api-client';
import { ApiResponse } from '@/types/common';
import {
  Wallet,
  WalletCharge,
  CoinTransaction,
  WalletBalanceResponse,
} from '@/types/wallet.types';

/**
 * Get wallet balance
 */
export async function getWalletBalance(): Promise<Wallet> {
  const response = await apiClient.get<ApiResponse<Wallet>>('/users/me/wallet/');
  return response.data.data;
}

/**
 * Charge wallet with coins
 */
export async function chargeWallet(data: WalletCharge): Promise<WalletBalanceResponse> {
  const response = await apiClient.post<ApiResponse<WalletBalanceResponse>>(
    '/wallet/charge/',
    data
  );
  return response.data.data;
}

/**
 * Get wallet transaction history
 */
export async function getWalletTransactions(): Promise<CoinTransaction[]> {
  const response = await apiClient.get<ApiResponse<CoinTransaction[]>>(
    '/users/me/wallet/transactions/'
  );
  return response.data.data;
}
