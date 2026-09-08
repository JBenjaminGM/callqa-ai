'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Phone, RefreshCw, UploadCloud } from 'lucide-react';
import { useAgents, useCalls } from '@/lib/queries';
import { getErrorMessage } from '@/lib/api';
import { Header } from '@/components/layout/header';
import { Card } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScoreBadge, StatusBadge } from '@/components/ui/badge';
import { EmptyState, ErrorState, Skeleton } from '@/components/ui/feedback';
import { callAgentName, formatDate, formatDuration } from '@/lib/utils';

/** Listado paginado de llamadas con filtros (ejecutivo, estado y fecha). */
export default function CallsPage() {
  const router = useRouter();
  const [agentId, setAgentId] = useState('');
  const [status, setStatus] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [page, setPage] = useState(1);

  const { data: agents } = useAgents();
  const { data, isLoading, error, refetch, isFetching } = useCalls({
    agent_id: agentId ? Number(agentId) : undefined,
    status: status || undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
    page,
    page_size: 20,
  });

  function resetPage<T>(setter: (v: T) => void) {
    return (v: T) => {
      setter(v);
      setPage(1);
    };
  }

  return (
    <>
      <Header title="Llamadas" />
      <main className="flex-1 overflow-y-auto p-6">
        {/* Filtros */}
        <div className="mb-5 flex flex-wrap items-end gap-3">
          <div className="w-48">
            <label className="mb-1.5 block text-small text-text-secondary">
              Ejecutivo
            </label>
            <Select
              value={agentId}
              onChange={(e) => resetPage(setAgentId)(e.target.value)}
            >
              <option value="">Todos</option>
              {agents?.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </Select>
          </div>
          <div className="w-44">
            <label className="mb-1.5 block text-small text-text-secondary">
              Estado
            </label>
            <Select
              value={status}
              onChange={(e) => resetPage(setStatus)(e.target.value)}
            >
              <option value="">Todos</option>
              <option value="QUEUED">En cola</option>
              <option value="TRANSCRIBING">Transcribiendo</option>
              <option value="ANALYZING">Analizando</option>
              <option value="DONE">Listo</option>
              <option value="ERROR">Error</option>
            </Select>
          </div>
          <div className="w-40">
            <label className="mb-1.5 block text-small text-text-secondary">
              Desde
            </label>
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => resetPage(setDateFrom)(e.target.value)}
            />
          </div>
          <div className="w-40">
            <label className="mb-1.5 block text-small text-text-secondary">
              Hasta
            </label>
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => resetPage(setDateTo)(e.target.value)}
            />
          </div>
          {(dateFrom || dateTo || agentId || status) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setAgentId('');
                setStatus('');
                setDateFrom('');
                setDateTo('');
                setPage(1);
              }}
            >
              Limpiar filtros
            </Button>
          )}
          <div className="ml-auto flex items-center gap-3">
            <Button
              variant="secondary"
              onClick={() => refetch()}
              disabled={isFetching}
              title="Actualizar estado de las llamadas"
            >
              <RefreshCw
                size={18}
                className={isFetching ? 'animate-spin' : undefined}
              />
              Actualizar
            </Button>
            <Link href="/calls/new">
              <Button>
                <UploadCloud size={18} />
                Subir llamadas
              </Button>
            </Link>
          </div>
        </div>

        {isLoading && (
          <div className="flex flex-col gap-2">
            {[0, 1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-14" />
            ))}
          </div>
        )}

        {error && <ErrorState message={getErrorMessage(error)} />}

        {data && data.items.length === 0 && (
          <EmptyState
            icon={<Phone size={48} />}
            title="No hay llamadas"
            description="No se encontraron llamadas con los filtros seleccionados."
          />
        )}

        {data && data.items.length > 0 && (
          <Card className="overflow-hidden !p-0">
            <table className="w-full text-body">
              <thead>
                <tr className="border-b border-border bg-bg-accent/40 text-left">
                  <th className="px-4 py-3 text-small text-text-secondary">
                    Ejecutivo
                  </th>
                  <th className="px-4 py-3 text-small text-text-secondary">
                    Subida
                  </th>
                  <th className="px-4 py-3 text-small text-text-secondary">
                    Duración
                  </th>
                  <th className="px-4 py-3 text-small text-text-secondary">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-small text-text-secondary">
                    Score
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((call) => (
                  <tr
                    key={call.id}
                    onClick={() => router.push(`/calls/${call.id}`)}
                    className="cursor-pointer border-b border-border
                               transition-colors last:border-0 hover:bg-bg-accent/30"
                  >
                    <td className="px-4 py-3 text-text-primary">
                      <span className="flex items-center gap-2">
                        {callAgentName(call)}
                        {!call.agent && call.detected_agent_name && (
                          <span
                            className="rounded-control bg-warning/15 px-1.5 py-0.5
                                       text-small font-medium text-warning"
                          >
                            Sin registrar
                          </span>
                        )}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-text-secondary">
                      {formatDate(call.created_at)}
                    </td>
                    <td className="px-4 py-3 font-mono text-text-secondary">
                      {formatDuration(call.duration_seconds)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={call.status} />
                    </td>
                    <td className="px-4 py-3">
                      {call.global_score != null ? (
                        <ScoreBadge score={call.global_score} />
                      ) : (
                        <span className="text-text-muted">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}

        {/* Paginación */}
        {data && data.total_pages > 1 && (
          <div className="mt-4 flex items-center justify-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Anterior
            </Button>
            <span className="text-small text-text-secondary">
              Página {data.page} de {data.total_pages}
            </span>
            <Button
              variant="ghost"
              size="sm"
              disabled={page >= data.total_pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Siguiente
            </Button>
          </div>
        )}
      </main>
    </>
  );
}
