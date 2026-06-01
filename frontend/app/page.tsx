'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import { Spinner } from '@/components/ui/feedback';

/** Página raíz: redirige al dashboard o al login según la sesión. */
export default function HomePage() {
  const router = useRouter();
  const token = useAuthStore((s) => s.token);

  useEffect(() => {
    router.replace(token ? '/dashboard' : '/login');
  }, [token, router]);

  return (
    <div className="flex h-screen items-center justify-center text-accent-primary">
      <Spinner className="h-8 w-8" />
    </div>
  );
}
