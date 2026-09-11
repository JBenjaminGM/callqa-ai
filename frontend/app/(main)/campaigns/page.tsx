'use client';

import { useRouter } from 'next/navigation';
import { Megaphone, Plus, FileText, FileUp } from 'lucide-react';
import { useCampaignList } from '@/lib/queries';
import { getErrorMessage } from '@/lib/api';
import { Header } from '@/components/layout/header';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { EmptyState, ErrorState, Skeleton } from '@/components/ui/feedback';

/** Listado de campañas y sus notas de producto. */
export default function CampaignsPage() {
  const router = useRouter();
  const { data: campaigns, isLoading, error } = useCampaignList();

  return (
    <>
      <Header title="Campañas" />
      <main className="flex-1 overflow-y-auto p-6">
        <div className="mb-5 flex items-center justify-between gap-3">
          <p className="text-body text-text-secondary">
            Notas de producto que la IA usa para evaluar la oferta de cada llamada
          </p>
          <Button onClick={() => router.push('/campaigns/new')}>
            <Plus size={18} />
            Nueva campaña
          </Button>
        </div>

        {isLoading && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <Skeleton key={i} className="h-28" />
            ))}
          </div>
        )}

        {error && <ErrorState message={getErrorMessage(error)} />}

        {campaigns && campaigns.length === 0 && (
          <EmptyState
            icon={<Megaphone size={48} />}
            title="Sin campañas"
            description="Crea la primera campaña rellenando el formulario con ayuda de la IA o subiendo una nota de producto en PDF."
            action={
              <Button onClick={() => router.push('/campaigns/new')}>
                <Plus size={18} />
                Nueva campaña
              </Button>
            }
          />
        )}

        {campaigns && campaigns.length > 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {campaigns.map((c) => (
              <Card
                key={c.id}
                onClick={() => router.push(`/campaigns/${c.id}`)}
                className="lift-on-hover cursor-pointer"
              >
                <div className="flex items-start gap-3">
                  <div
                    className="flex h-11 w-11 shrink-0 items-center justify-center rounded-control
                               bg-accent-primary/15 text-accent-primary"
                  >
                    <Megaphone size={20} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <CardTitle className="truncate text-body font-semibold">
                        {c.name}
                      </CardTitle>
                      {!c.active && (
                        <span className="rounded-control bg-danger/15 px-2 py-0.5 text-small text-danger">
                          Inactiva
                        </span>
                      )}
                    </div>
                    <p className="mt-0.5 truncate text-small text-text-muted">
                      {c.product_service ?? c.offer_description ?? 'Sin descripción'}
                    </p>
                    <div className="mt-2 flex items-center gap-3 text-small text-text-secondary">
                      <span className="inline-flex items-center gap-1">
                        {c.source === 'pdf' ? (
                          <FileUp size={13} />
                        ) : (
                          <FileText size={13} />
                        )}
                        {c.source === 'pdf'
                          ? 'PDF'
                          : c.source === 'migrated'
                            ? 'Migrada'
                            : 'Formulario'}
                      </span>
                      <span>· {c.calls_count ?? 0} llamada(s)</span>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
