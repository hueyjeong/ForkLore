import axios, { type InternalAxiosRequestConfig, type AxiosResponse } from 'axios';
import { getCookie, setCookie, deleteCookie } from 'cookies-next';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Access Token 주입
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getCookie('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (error: any) => Promise.reject(error)
);

// Response Interceptor: 401 에러 시 Refresh Token으로 재시도
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async (error: any) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = getCookie('refresh_token');
        if (!refreshToken) {
          throw new Error('Refresh token not found');
        }

        // Silent Refresh API 호출
        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refreshToken,
        });

        const { accessToken: newAccessToken } = data;
        setCookie('access_token', newAccessToken);
        
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh 실패 시 로그아웃 처리
        deleteCookie('access_token');
        deleteCookie('refresh_token');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
