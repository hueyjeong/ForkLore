export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  serverTime?: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface PageParams {
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, string[]>;
}
