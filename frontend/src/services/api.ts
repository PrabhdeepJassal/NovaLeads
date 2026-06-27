// ============================================================
// NovaLeads — Axios API Client
// ============================================================

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — attach auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('lp_access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle 401, refresh token, global errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // If 401 and we haven't retried yet, attempt token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('lp_refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/auth/refresh', {
            refresh_token: refreshToken,
          });
          localStorage.setItem('lp_access_token', data.access_token);
          if (data.refresh_token) {
            localStorage.setItem('lp_refresh_token', data.refresh_token);
          }
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          }
          return api(originalRequest);
        } catch {
          // Refresh failed — clear everything
          localStorage.removeItem('lp_access_token');
          localStorage.removeItem('lp_refresh_token');
          localStorage.removeItem('lp_user');
          window.location.href = '/login';
          return Promise.reject(error);
        }
      } else {
        localStorage.removeItem('lp_access_token');
        localStorage.removeItem('lp_user');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Helper to extract readable error message
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (typeof data === 'string') return data;
    if (data?.detail) return data.detail;
    if (typeof data === 'object') {
      // Handle DRF-style field errors
      const messages: string[] = [];
      for (const [, value] of Object.entries(data)) {
        if (Array.isArray(value)) messages.push(value.join(' '));
        else if (typeof value === 'string') messages.push(value);
      }
      if (messages.length > 0) return messages.join('\n');
    }
    return error.message || 'An unexpected error occurred';
  }
  if (error instanceof Error) return error.message;
  return 'An unexpected error occurred';
}

export default api;
