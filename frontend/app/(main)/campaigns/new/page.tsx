'use client';

import { useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, FileUp, Save, Sparkles, X } from 'lucide-react';
import {
  useAssistCampaign,
  useCreateCampaign,
  useExtractCampaignPdf,
} from '@/lib/queries';
import { getErrorMessage } from '@/lib/api';
import { Header } from '@/components/layout/header';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Spinner, ErrorState } from '@/components/ui/feedback';
import {
  CampaignFields,
  type CampaignFormState,
  emptyCampaignForm,
  formToDraft,
  formToPayload,
  mergeDraftIntoForm,
} from '@/components/campaigns/campaign-form';

/** Alta de una campaña: por formulario (con IA) o subiendo una nota de producto en PDF. */
export default function NewCampaignPage() {
  const router = useRouter();
  const extract = useExtractCampaignPdf();
  const assist = useAssistCampaign();
  const create = useCreateCampaign();

  const [form, setForm] = useState<CampaignFormState>(emptyCampaignForm());
  const [missing, setMissing] = useState<string[]>([]);
  const [description, setDescription] = useState('');
  const [sourceFile, setSourceFile] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  async function onPickPdf(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    setError(null);
    setInfo(null);
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('El archivo debe ser un PDF.');
      return;
    }
    try {
      const res = await extract.mutateAsync(file);
      setForm((f) => mergeDraftIntoForm(res.draft, f));
      setMissing(res.missing_fields ?? []);
      setSourceFile(res.source_filename ?? file.name);
      setInfo(
        res.warning ??
          'Nota de producto extraída del PDF. Revisa y completa los campos marcados.',
      );
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function onAssist() {
    if (!description.trim()) {
      setError('Escribe una breve descripción de la campaña para que la IA ayude.');
      return;
    }
    setError(null);
    setInfo(null);
    try {
      const res = await assist.mutateAsync({
        description: description.trim(),
        current: formToDraft(form),
      });
      setForm((f) => mergeDraftIntoForm(res.draft, f));
      setInfo(res.warning ?? 'La IA completó la nota de producto. Revisa y ajusta lo necesario.');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!form.name.trim()) {
      setError('El nombre de la campaña es obligatorio.');
      return;
    }
    try {
      const created = await create.mutateAsync({
        ...formToPayload(form),
        source: sourceFile ? 'pdf' : 'form',
        source_filename: sourceFile ?? undefined,
      } as never);
      router.push(`/campaigns/${created.id}`);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <>
      <Header title="Nueva campaña" />
      <main className="flex-1 overflow-y-auto p-6">
        <button
          onClick={() => router.push('/campaigns')}
          className="mb-4 flex items-center gap-1.5 text-small text-text-secondary
                     transition-colors hover:text-accent-primary"
        >
          <ArrowLeft size={16} />
          Volver a campañas
        </button>

        <form onSubmit={onSubmit} className="mx-auto flex max-w-3xl flex-col gap-5">
          {/* Importar PDF */}
          <Card className="flex flex-col gap-3">
            <div>
              <CardTitle>Opción 1 · Subir nota de producto (PDF)</CardTitle>
              <p className="mt-1 text-small text-text-secondary">
                La IA leerá el PDF y completará la nota. Lo que no encuentre lo
                pedirá abajo en el formulario.
              </p>
            </div>
            <input
              ref={fileRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={onPickPdf}
            />
            <div className="flex flex-wrap items-center gap-3">
              <Button
                type="button"
                variant="secondary"
                onClick={() => fileRef.current?.click()}
                disabled={extract.isPending}
              >
                {extract.isPending ? <Spinner /> : <FileUp size={16} />}
                Seleccionar PDF
              </Button>
              {sourceFile && (
                <span className="inline-flex items-center gap-1 text-small text-text-secondary">
                  {sourceFile}
                  <button
                    type="button"
                    aria-label="Quitar PDF"
                    onClick={() => {
                      setSourceFile(null);
                      setMissing([]);
                    }}
                    className="text-text-muted hover:text-danger"
                  >
                    <X size={14} />
                  </button>
                </span>
              )}
            </div>
          </Card>

          {/* Asistente IA */}
          <Card className="flex flex-col gap-3">
            <div>
              <CardTitle>Opción 2 · Describe la campaña y deja que la IA la redacte</CardTitle>
              <p className="mt-1 text-small text-text-secondary">
                Escribe en pocas líneas la oferta; la IA propondrá la nota de
                producto estructurada.
              </p>
            </div>
            <div>
              <Label htmlFor="description">Descripción de la campaña</Label>
              <Textarea
                id="description"
                rows={3}
                placeholder="Ej. Tarjeta de crédito Oro sin cuota el primer año, con 2% de cashback y sala VIP, para clientes con ingresos altos…"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div>
              <Button
                type="button"
                variant="secondary"
                onClick={onAssist}
                disabled={assist.isPending}
              >
                {assist.isPending ? <Spinner /> : <Sparkles size={16} />}
                Completar con IA
              </Button>
            </div>
          </Card>

          {info && (
            <div className="rounded-card border border-info/30 bg-info/10 px-4 py-3 text-body text-info">
              {info}
            </div>
          )}

          {/* Formulario de la nota de producto */}
          <Card className="flex flex-col gap-5">
            <div>
              <CardTitle>Nota de producto</CardTitle>
              <p className="mt-1 text-small text-text-secondary">
                Esta es la plantilla que la IA usará para evaluar si el ejecutivo
                ofreció lo correcto en cada llamada de la campaña.
              </p>
            </div>

            <CampaignFields value={form} onChange={setForm} highlight={missing} />

            {error && <ErrorState message={error} />}

            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="ghost"
                onClick={() => router.push('/campaigns')}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={create.isPending}>
                {create.isPending ? <Spinner /> : <Save size={18} />}
                Crear campaña
              </Button>
            </div>
          </Card>
        </form>
      </main>
    </>
  );
}
