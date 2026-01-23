export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  serverTime?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
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
