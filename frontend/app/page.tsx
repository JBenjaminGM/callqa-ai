'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isManager, useAuthHydrated, useAuthStore } from '@/lib/auth';
import { Spinner } from '@/components/ui/feedback';

/**
 * Página raíz: redirige según la sesión.
 *
 * Espera a que `persist` haya rehidratado el store: en el primer render el token
 * siempre es null, así que decidir antes mandaría al login a alguien con sesión.
 */
export default function HomePage() {
  const router = useRouter();
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);
  const hydrated = useAuthHydrated();

  useEffect(() => {
    if (!hydrated) return;
    if (!token) {
      router.replace('/login');
      return;
    }
    router.replace(isManager(user) ? '/dashboard' : '/mi-panel');
  }, [hydrated, token, user, router]);

  return (
    <div className="flex h-screen items-center justify-center text-accent-primary">
      <Spinner className="h-8 w-8" />
    </div>
  );
}
