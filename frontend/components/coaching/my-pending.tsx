'use client';

import Link from 'next/link';
import { Inbox } from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { useMyPending } from '@/lib/queries';
import { formatDate, scoreColor } from '@/lib/utils';

/**
 * Las evaluaciones que el asesor todavía no ha leído.
 *
 * Va lo primero en su panel, antes que las medias: lo urgente para él no es su
 * promedio del trimestre, es que hay tres llamadas suyas evaluadas que aún no
 * ha visto.
 */
export function MyPendingEvaluations({ enabled = true }: { enabled?: boolean }) {
  const { data } = useMyPending(enabled);

  // Sin nada pendiente no se ocupa sitio con una tarjeta vacía.
  if (!data?.length) return null;

  return (
    <Card className="ring-1 ring-accent-primary/30">
      <CardTitle className="mb-1 flex items-center gap-2">
        <Inbox size={18} className="text-accent-primary" />
        {data.length === 1
          ? 'Tienes 1 evaluación sin leer'
          : `Tienes ${data.length} evaluaciones sin leer`}
      </CardTitle>
      <p className="mb-4 text-small text-text-secondary">
        Ábrelas para ver el detalle y responder. Si crees que una nota no es
        justa, ahí mismo puedes pedir que la revise tu jefe de área.
      </p>
      <ul className="flex flex-col gap-2">
        {data.slice(0, 6).map((c) => (
          <li key={c.call_id}>
            <Link
              href={`/calls/${c.call_id}`}
              className="flex items-center gap-3 rounded-card border border-border
                         bg-bg-secondary px-3 py-2.5 transition-colors
                         hover:border-accent-primary"
            >
              <span className="font-mono text-small text-text-muted">
                #{c.call_id}
              </span>
              <span className="min-w-0 flex-1 truncate text-small text-text-primary">
                {c.campaign ?? 'Sin campaña'}
                {c.call_date ? ` · ${formatDate(c.call_date)}` : ''}
              </span>
              <span
                className="font-mono text-body font-semibold tabular-nums"
                style={{ color: scoreColor(c.global_score) }}
              >
                {c.global_score}
              </span>
            </Link>
          </li>
        ))}
      </ul>
      {data.length > 6 && (
        <p className="mt-3 text-small text-text-muted">
          Y {data.length - 6} más en{' '}
          <Link href="/calls" className="text-accent-primary hover:underline">
            Mis llamadas
          </Link>
          .
        </p>
      )}
    </Card>
  );
}
