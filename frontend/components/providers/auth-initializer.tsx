'use client'

import { useEffect } from 'react'
import { useAuthStore } from '@/stores/auth-store'

/**
 * AuthInitializer - Thin wrapper for Zustand auth store initialization
 *
 * Calls refreshUser on mount to restore auth state from cookies.
 * This replaces the old AuthProvider React Context with direct Zustand calls.
 */
export function AuthInitializer({ children }: { children: React.ReactNode }) {
  const refreshUser = useAuthStore((state) => state.refreshUser)

  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  return <>{children}</>
}
