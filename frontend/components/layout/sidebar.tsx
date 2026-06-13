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

/** Barra lateral de navegación principal. */
export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="flex w-60 shrink-0 flex-col gap-1 border-r border-border
                 bg-[var(--glass-bg)] p-3 backdrop-blur-xl"
    >
      <div className="mb-4 flex items-center gap-2.5 px-2 py-3">
        <div
          className="flex h-9 w-9 items-center justify-center rounded-lg
                     bg-accent-primary text-lg font-extrabold text-white"
        >
          Q
        </div>
        <div>
          <p className="text-h3 font-extrabold text-text-primary">CallQA AI</p>
          <p className="text-small font-semibold lowercase tracking-wide text-accent-primary">
            minsait
          </p>
        </div>
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
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-body',
                'transition-colors',
                active
                  ? 'bg-accent-primary text-white shadow-[0_0_20px_var(--glow)]'
                  : 'text-text-secondary hover:bg-bg-accent/50',
              )}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
