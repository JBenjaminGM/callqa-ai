'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Phone,
  Users,
  Megaphone,
  Settings,
  UploadCloud,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/calls', label: 'Llamadas', icon: Phone },
  { href: '/calls/new', label: 'Nueva llamada', icon: UploadCloud },
  { href: '/agents', label: 'Ejecutivos', icon: Users },
  { href: '/campaigns', label: 'Campañas', icon: Megaphone },
  { href: '/settings', label: 'Configuración', icon: Settings },
];

/** Barra lateral de navegación — fondo Pruno con el logo blanco Minsait (negativo). */
export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-60 shrink-0 flex-col bg-[var(--pruno)] p-3 text-white">
      {/* Lockup de marca: logo blanco Minsait + nombre del producto */}
      <div className="mb-6 px-2 pt-4">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/brand/minsait-logo-blanco.svg"
          alt="Minsait"
          width={150}
          height={15}
          className="h-auto w-[150px]"
        />
        <p className="destacado mt-3 text-[11px] text-white/55">CallQA AI</p>
      </div>

      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active =
            href === '/calls'
              ? pathname === '/calls'
              : pathname === href ||
                (href !== '/dashboard' &&
                  href !== '/calls/new' &&
                  pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-body transition-colors',
                active
                  ? 'bg-[var(--fucsia)] font-bold text-[var(--pruno-oscuro)]'
                  : 'text-white/75 hover:bg-white/10 hover:text-white',
              )}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>

      <p className="mt-auto px-3 pb-2 text-[11px] lowercase tracking-wide text-white/45">
        tech for <span className="text-[var(--fucsia)]">impact</span>
      </p>
    </aside>
  );
}
