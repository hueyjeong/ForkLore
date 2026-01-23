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
  size?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export type JsonValue = string | number | boolean | null | { [key: string]: JsonValue } | JsonValue[];

export interface ErrorResponse {
  success: false;
  message: string;
  errors?: Record<string, string | string[]>;
  timestamp: string;
}
