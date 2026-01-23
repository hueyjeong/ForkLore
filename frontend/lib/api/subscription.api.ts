import { apiClient } from '@/lib/api-client';
import { ApiResponse } from '@/types/common';
import {
  Subscription,
  SubscriptionCreate,
} from '@/types/subscription.types';
import axios from 'axios';

const BASE_URL = '/subscriptions/';

/**
 * Get current subscription status
 */
export async function getSubscriptionStatus(): Promise<Subscription | null> {
  try {
    const response = await apiClient.get<ApiResponse<Subscription>>(
      BASE_URL
    );
    return response.data.data;
  } catch (error: unknown) {
    // Return null if 404 (not found/not subscribed)
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw error;
  }
}

/**
 * Subscribe to a plan
 */
export async function subscribe(data: SubscriptionCreate): Promise<Subscription> {
  const response = await apiClient.post<ApiResponse<Subscription>>(
    BASE_URL,
    data
  );
  return response.data.data;
}

/**
 * Cancel subscription
 */
export async function cancelSubscription(subscriptionId: number): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`${BASE_URL}${subscriptionId}/`);
}
