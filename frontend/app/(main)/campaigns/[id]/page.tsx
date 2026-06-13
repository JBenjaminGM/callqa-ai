'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Save, Trash2 } from 'lucide-react';
import {
  useCampaign,
  useDeactivateCampaign,
  useUpdateCampaign,
} from '@/lib/queries';
import { getErrorMessage } from '@/lib/api';
import { Header } from '@/components/layout/header';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ErrorState, Skeleton, Spinner } from '@/components/ui/feedback';
import {
  CampaignFields,
  type CampaignFormState,
  campaignToForm,
  emptyCampaignForm,
  formToPayload,
} from '@/components/campaigns/campaign-form';

/** Detalle y edición de una campaña y su nota de producto. */
export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);

  const { data: campaign, isLoading, error } = useCampaign(id);
  const update = useUpdateCampaign();
  const deactivate = useDeactivateCampaign();

  const [form, setForm] = useState<CampaignFormState>(emptyCampaignForm());
  const [formError, setFormError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  // Carga la campaña en el formulario al recibir los datos.
  useEffect(() => {
    if (campaign) setForm(campaignToForm(campaign));
  }, [campaign]);

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    setSaved(false);
    if (!form.name.trim()) {
      setFormError('El nombre de la campaña es obligatorio.');
      return;
    }
    try {
      await update.mutateAsync({ id, ...formToPayload(form) } as never);
      setSaved(true);
    } catch (err) {
      setFormError(getErrorMessage(err));
    }
  }

  async function onDeactivate() {
    if (!confirm('¿Desactivar esta campaña? Dejará de aparecer al subir llamadas.')) {
      return;
    }
    await deactivate.mutateAsync(id);
    router.push('/campaigns');
  }

  return (
    <>
      <Header title="Campaña" />
      <main className="flex-1 overflow-y-auto p-6">
        <button
          onClick={() => router.push('/campaigns')}
          className="mb-4 flex items-center gap-1.5 text-small text-text-secondary
                     transition-colors hover:text-accent-primary"
        >
          <ArrowLeft size={16} />
          Volver a campañas
        </button>

        {isLoading && <Skeleton className="h-64" />}
        {error && <ErrorState message={getErrorMessage(error)} />}

        {campaign && (
          <form onSubmit={onSave} className="mx-auto flex max-w-3xl flex-col gap-5">
            <Card className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-h3 text-text-primary">{campaign.name}</p>
                <p className="text-small text-text-secondary">
                  {campaign.calls_count ?? 0} llamada(s) usando esta campaña
                  {!campaign.active && ' · Inactiva'}
                </p>
              </div>
              {campaign.active && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={onDeactivate}
                  disabled={deactivate.isPending}
                >
                  <Trash2 size={16} />
                  Desactivar
                </Button>
              )}
            </Card>

            <Card className="flex flex-col gap-5">
              <div>
                <CardTitle>Nota de producto</CardTitle>
                <p className="mt-1 text-small text-text-secondary">
                  La IA evalúa cada llamada de esta campaña contra esta plantilla.
                </p>
              </div>

              <CampaignFields value={form} onChange={setForm} />

              {formError && <ErrorState message={formError} />}
              {saved && (
                <div className="rounded-lg border border-success/30 bg-success/10 px-4 py-3 text-body text-success">
                  Cambios guardados.
                </div>
              )}

              <div className="flex justify-end">
                <Button type="submit" disabled={update.isPending}>
                  {update.isPending ? <Spinner /> : <Save size={18} />}
                  Guardar cambios
                </Button>
              </div>
            </Card>
          </form>
        )}
      </main>
    </>
  );
}
