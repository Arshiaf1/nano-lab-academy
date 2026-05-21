const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface FetchOptions extends RequestInit {
  requiresAuth?: boolean;
}

/**
 * API client wrapper that automatically attaches JWT token to requests
 * and handles token refresh logic
 */
async function apiClient(
  endpoint: string,
  options: FetchOptions = {}
): Promise<Response> {
  const { requiresAuth = true, ...fetchOptions } = options;

  let token = null;
  if (requiresAuth) {
    token = localStorage.getItem('token');
  }

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  // Handle token refresh if 401 response
  if (response.status === 401 && token) {
    try {
      const refreshResponse = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: token }),
      });

      if (refreshResponse.ok) {
        const data = await refreshResponse.json();
        localStorage.setItem('token', data.access_token);

        // Retry original request with new token
        const retryHeaders: HeadersInit = {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${data.access_token}`,
          ...(fetchOptions.headers || {}),
        };

        response = await fetch(`${API_URL}${endpoint}`, {
          ...fetchOptions,
          headers: retryHeaders,
        });
      }
    } catch {
      // Token refresh failed, let the app handle the 401
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }

  return response;
}

/**
 * Helper function to make API calls with automatic error handling
 */
export async function apiCall<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const response = await apiClient(endpoint, options);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

/**
 * GET request helper
 */
export function apiGet<T>(endpoint: string, options: FetchOptions = {}) {
  return apiCall<T>(endpoint, { ...options, method: 'GET' });
}

/**
 * POST request helper
 */
export function apiPost<T>(endpoint: string, body: unknown, options: FetchOptions = {}) {
  return apiCall<T>(endpoint, {
    ...options,
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * PUT request helper
 */
export function apiPut<T>(endpoint: string, body: unknown, options: FetchOptions = {}) {
  return apiCall<T>(endpoint, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

/**
 * DELETE request helper
 */
export function apiDelete<T>(endpoint: string, options: FetchOptions = {}) {
  return apiCall<T>(endpoint, {
    ...options,
    method: 'DELETE',
  });
}
