'use client';

import axios, { AxiosError } from 'axios';
import { getToken, useAuthStore } from '@/lib/auth';

/**
 * Instancia de Axios configurada para hablar con el backend de CallQA AI.
 *
 * - Añade automáticamente el token JWT en cada petición.
 * - Si el backend responde 401, limpia la sesión y redirige al login.
 */
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1',
  timeout: 60000,
});

// Interceptor de petición: añade la cabecera Authorization.
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor de respuesta: gestiona el 401 (sesión expirada).
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      useAuthStore.getState().clearSession();
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

/** Extrae un mensaje de error legible de una excepción de Axios. */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
    return error.message;
  }
  return 'Ocurrió un error inesperado.';
}
