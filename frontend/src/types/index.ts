/**
 * Shared TypeScript types used across the application.
 */

export interface HealthResponse {
  success: boolean;
  status: string;
  app_name: string;
  version: string;
  environment: string;
  timestamp: string;
}

export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface ApiErrorResponse {
  success: false;
  error: ApiErrorDetail;
}

export type NavItem = {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string | number;
};
