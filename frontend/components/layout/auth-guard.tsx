'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import { Spinner } from '@/components/ui/feedback';

/**
 * Protege las páginas autenticadas.
 *
 * Si no hay token tras la hidratación de Zustand, redirige al login.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const token = useAuthStore((s) => s.token);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Espera a que el store persistido se hidrate antes de decidir.
    if (!token) {
      router.replace('/login');
    } else {
      setReady(true);
    }
  }, [token, router]);

  if (!ready) {
    return (
      <div className="flex h-screen items-center justify-center text-accent-primary">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  return <>{children}</>;
}
