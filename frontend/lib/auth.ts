'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';

/**
 * Estado de autenticación, persistido en localStorage.
 *
 * Guarda el token JWT y el usuario para mantener la sesión entre recargas.
 */
interface AuthState {
  token: string | null;
  user: User | null;
  setSession: (token: string, user: User) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setSession: (token, user) => set({ token, user }),
      clearSession: () => set({ token: null, user: null }),
    }),
    { name: 'callqa-auth' },
  ),
);

/** Devuelve el token actual leyendo directamente del store (uso fuera de React). */
export function getToken(): string | null {
  return useAuthStore.getState().token;
}
