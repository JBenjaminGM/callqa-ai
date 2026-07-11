'use client';

import { useRouter } from 'next/navigation';
import { LogOut } from 'lucide-react';
import { useAuthStore } from '@/lib/auth';
import { ThemeToggle } from './theme-toggle';

/** Cabecera superior: título, toggle de tema, usuario y logout. */
export function Header({ title }: { title: string }) {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const clearSession = useAuthStore((s) => s.clearSession);

  function logout() {
    clearSession();
    router.replace('/login');
  }

  const initials = (user?.name ?? 'U')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <header
      className="flex h-16 shrink-0 items-center justify-between border-b
                 border-border bg-[var(--glass-bg)] px-6"
    >
      <h1 className="text-h2 text-text-primary">{title}</h1>

      <div className="flex items-center gap-3">
        <ThemeToggle />

        <div className="flex items-center gap-2">
          <div
            className="flex h-9 w-9 items-center justify-center rounded-full
                       bg-accent-secondary text-small font-bold text-white"
          >
            {initials}
          </div>
          <div className="hidden sm:block">
            <p className="text-small font-medium text-text-primary">
              {user?.name ?? 'Usuario'}
            </p>
            <p className="text-small text-text-muted">{user?.email}</p>
          </div>
        </div>

        <button
          onClick={logout}
          aria-label="Cerrar sesión"
          className="flex h-10 w-10 items-center justify-center rounded-lg
                     text-text-secondary transition-colors hover:bg-bg-accent/40"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
