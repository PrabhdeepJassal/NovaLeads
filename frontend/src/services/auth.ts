// ============================================================
// NovaLeads — Auth Service
// ============================================================

import api from './api';
import type { AuthResponse, LoginCredentials, RegisterData, User } from '../types';

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/auth/login', credentials);
  localStorage.setItem('lp_access_token', data.access_token);
  localStorage.setItem('lp_refresh_token', data.refresh_token);
  localStorage.setItem('lp_user', JSON.stringify(data.user));
  return data;
}

export async function register(regData: RegisterData): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>('/auth/register', regData);
  localStorage.setItem('lp_access_token', data.access_token);
  localStorage.setItem('lp_refresh_token', data.refresh_token);
  localStorage.setItem('lp_user', JSON.stringify(data.user));
  return data;
}

export async function refreshToken(refresh: string): Promise<{ access_token: string; refresh_token?: string }> {
  const { data } = await api.post<{ access_token: string; refresh_token?: string }>('/auth/refresh', { refresh_token: refresh });
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>('/auth/me');
  return data;
}

export async function updateProfile(profileData: Partial<User & { current_password?: string; new_password?: string }>): Promise<User> {
  const { data } = await api.patch<User>('/auth/me', profileData);
  return data;
}

export function logout(): void {
  localStorage.removeItem('lp_access_token');
  localStorage.removeItem('lp_refresh_token');
  localStorage.removeItem('lp_user');
}

export function getStoredUser(): User | null {
  const stored = localStorage.getItem('lp_user');
  if (stored) {
    try {
      return JSON.parse(stored) as User;
    } catch {
      return null;
    }
  }
  return null;
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem('lp_access_token');
}
