'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { LogIn } from 'lucide-react';
import { api, getErrorMessage } from '@/lib/api';
import { useAuthStore } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Spinner } from '@/components/ui/feedback';
import { PrototypeBanner } from '@/components/layout/prototype-banner';
import type { TokenResponse } from '@/types';

const loginSchema = z.object({
  email: z.string().email('Introduce un email válido.'),
  password: z.string().min(1, 'La contraseña es obligatoria.'),
});

type LoginForm = z.infer<typeof loginSchema>;

/** Página de inicio de sesión. */
export default function LoginPage() {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: LoginForm) {
    setServerError(null);
    try {
      const { data } = await api.post<TokenResponse>('/auth/login', values);
      setSession(data.access_token, data.user);
      // El asesor va a su panel personal; admin/jefe al dashboard global.
      router.replace(data.user.role === 'asesor' ? '/mi-panel' : '/dashboard');
    } catch (error) {
      setServerError(getErrorMessage(error));
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-bg-primary">
      <PrototypeBanner />
      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-md animate-fade-in">
          {/* Contenedor achaflanado con la marca Minsait y el dispositivo de titular */}
          <div className="chamfer bg-bg-card p-8 sm:p-10">
            {/* Logo Minsait: positivo (Pruno) en claro, blanco en oscuro */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/minsait-logo-pruno.svg"
              alt="Minsait"
              width={160}
              height={16}
              className="block h-auto w-[160px] dark:hidden"
            />
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/minsait-logo-blanco.svg"
              alt="Minsait"
              width={160}
              height={16}
              className="hidden h-auto w-[160px] dark:block"
            />

            {/* Titular: minúscula, palabra clave en Fucsia, sin punto final */}
            <h1 className="mt-7 text-display text-text-primary">
              calidad con
              <br />
              <span className="hl">impacto</span>
            </h1>
            <p className="destacado mt-3 text-[11px] text-text-muted">
              CallQA AI · Quality Assurance con IA
            </p>

            {/* Formulario */}
            <form onSubmit={handleSubmit(onSubmit)} className="mt-8">
              <div className="mb-4">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@callqa.com"
                autoComplete="email"
                {...register('email')}
              />
              {errors.email && (
                <p className="mt-1 text-small text-danger">
                  {errors.email.message}
                </p>
              )}
            </div>

            <div className="mb-5">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                autoComplete="current-password"
                {...register('password')}
              />
              {errors.password && (
                <p className="mt-1 text-small text-danger">
                  {errors.password.message}
                </p>
              )}
            </div>

            {serverError && (
              <p className="mb-4 rounded-lg bg-danger/10 px-3 py-2 text-small text-danger">
                {serverError}
              </p>
            )}

            <Button
              type="submit"
              size="lg"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? <Spinner /> : <LogIn size={18} />}
              Entrar
            </Button>
          </form>
          </div>
        </div>
      </div>
    </div>
  );
}
