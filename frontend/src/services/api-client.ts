/**
 * API client for communicating with the AURA AI backend.
 * Provides typed request methods with error handling.
 */

import { API } from "@/lib/constants";

class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details: Record<string, unknown> = {},
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface ApiErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: ApiErrorResponse | null = null;
    try {
      errorData = await response.json();
    } catch {
      // Response body is not JSON
    }

    throw new ApiError(
      response.status,
      errorData?.error?.code ?? "UNKNOWN_ERROR",
      errorData?.error?.message ?? `Request failed with status ${response.status}`,
      errorData?.error?.details ?? {},
    );
  }

  return response.json() as Promise<T>;
}

function buildUrl(path: string): string {
  return `${API.BASE_URL}${API.V1_PREFIX}${path}`;
}

function defaultHeaders(): HeadersInit {
  return {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
}

export const apiClient = {
  async get<T>(path: string, signal?: AbortSignal): Promise<T> {
    const response = await fetch(buildUrl(path), {
      method: "GET",
      headers: defaultHeaders(),
      signal,
    });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
    const response = await fetch(buildUrl(path), {
      method: "POST",
      headers: defaultHeaders(),
      body: JSON.stringify(body),
      signal,
    });
    return handleResponse<T>(response);
  },

  async put<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
    const response = await fetch(buildUrl(path), {
      method: "PUT",
      headers: defaultHeaders(),
      body: JSON.stringify(body),
      signal,
    });
    return handleResponse<T>(response);
  },

  async patch<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
    const response = await fetch(buildUrl(path), {
      method: "PATCH",
      headers: defaultHeaders(),
      body: JSON.stringify(body),
      signal,
    });
    return handleResponse<T>(response);
  },

  async delete<T>(path: string, signal?: AbortSignal): Promise<T> {
    const response = await fetch(buildUrl(path), {
      method: "DELETE",
      headers: defaultHeaders(),
      signal,
    });
    return handleResponse<T>(response);
  },
};

export { ApiError };
export type { ApiErrorResponse };
