'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { getCookie, deleteCookie, setCookie } from 'cookies-next';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  nickname: string;
  avatarUrl?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (accessToken: string, refreshToken: string, user: User) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const logout = useCallback(() => {
    deleteCookie('access_token');
    deleteCookie('refresh_token');
    setUser(null);
    router.push('/login');
  }, [router]);

  const refreshUser = useCallback(async () => {
    const token = getCookie('access_token');
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const { data } = await apiClient.get<User>('/auth/me');
      setUser(data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      // Don't logout immediately on me fetch failure as interceptor handles 401
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback((accessToken: string, refreshToken: string, userData: User) => {
    setCookie('access_token', accessToken);
    setCookie('refresh_token', refreshToken);
    setUser(userData);
    router.push('/');
  }, [router]);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
