'use client';

import { useEffect, useState } from 'react';
import { Save } from 'lucide-react';
import {
  useRubric,
  useSettings,
  useUpdateRubric,
  useUpdateSettings,
} from '@/lib/queries';
import { getErrorMessage } from '@/lib/api';
import { Header } from '@/components/layout/header';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { ErrorState, Skeleton, Spinner } from '@/components/ui/feedback';

const LANGUAGES = [
  { code: 'es', label: 'Español' },
  { code: 'en', label: 'Inglés' },
  { code: 'pt', label: 'Portugués' },
  { code: 'fr', label: 'Francés' },
];

/** Página de configuración: rúbrica de evaluación e idioma de análisis. */
export default function SettingsPage() {
  const { data: rubric, isLoading: rubricLoading, error: rubricError } =
    useRubric();
  const { data: settings } = useSettings();
  const updateRubric = useUpdateRubric();
  const updateSettings = useUpdateSettings();

  // Estado local de los pesos de la rúbrica.
  const [weights, setWeights] = useState<Record<string, number>>({});
  const [language, setLanguage] = useState('es');
  const [rubricMsg, setRubricMsg] = useState<string | null>(null);
  const [rubricErr, setRubricErr] = useState<string | null>(null);
  const [settingsMsg, setSettingsMsg] = useState<string | null>(null);

  useEffect(() => {
    if (rubric) {
      const initial: Record<string, number> = {};
      rubric.forEach((d) => {
        initial[d.dimension_key] = Number(d.weight);
      });
      setWeights(initial);
    }
  }, [rubric]);

  useEffect(() => {
    if (settings) setLanguage(settings.default_language);
  }, [settings]);

  const total = Object.values(weights).reduce((a, b) => a + b, 0);

  async function saveRubric() {
    setRubricMsg(null);
    setRubricErr(null);
    if (Math.abs(total - 100) > 0.5) {
      setRubricErr(
        `Los pesos deben sumar 100%. Suma actual: ${total.toFixed(2)}%.`,
      );
      return;
    }
    try {
      await updateRubric.mutateAsync(
        Object.entries(weights).map(([dimension_key, weight]) => ({
          dimension_key,
          weight,
        })),
      );
      setRubricMsg('Rúbrica actualizada correctamente.');
    } catch (err) {
      setRubricErr(getErrorMessage(err));
    }
  }

  async function saveLanguage() {
    setSettingsMsg(null);
    try {
      await updateSettings.mutateAsync({ default_language: language });
      setSettingsMsg('Idioma de análisis actualizado.');
    } catch (err) {
      setSettingsMsg(getErrorMessage(err));
    }
  }

  return (
    <>
      <Header title="Configuración" />
      <main className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto flex max-w-2xl flex-col gap-6">
          {/* Rúbrica */}
          <Card>
            <CardTitle className="mb-1">Rúbrica de evaluación</CardTitle>
            <p className="mb-4 text-small text-text-secondary">
              Ajusta el peso de cada dimensión. La suma debe ser exactamente
              100%.
            </p>

            {rubricLoading && (
              <div className="flex flex-col gap-2">
                {[0, 1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-10" />
                ))}
              </div>
            )}
            {rubricError && (
              <ErrorState message={getErrorMessage(rubricError)} />
            )}

            {rubric && (
              <div className="flex flex-col gap-3">
                {rubric.map((dim) => (
                  <div
                    key={dim.dimension_key}
                    className="flex items-center justify-between gap-4"
                  >
                    <span className="text-body text-text-primary">
                      {dim.dimension_name}
                    </span>
                    <div className="flex w-28 items-center gap-1">
                      <Input
                        type="number"
                        min={0}
                        max={100}
                        step="0.01"
                        value={weights[dim.dimension_key] ?? 0}
                        onChange={(e) =>
                          setWeights((w) => ({
                            ...w,
                            [dim.dimension_key]: Number(e.target.value),
                          }))
                        }
                      />
                      <span className="text-small text-text-muted">%</span>
                    </div>
                  </div>
                ))}

                <div className="mt-2 flex items-center justify-between border-t border-border pt-3">
                  <span className="text-body font-semibold text-text-primary">
                    Total
                  </span>
                  <span
                    className={
                      Math.abs(total - 100) > 0.5
                        ? 'text-body font-bold text-danger'
                        : 'text-body font-bold text-success'
                    }
                  >
                    {total.toFixed(2)}%
                  </span>
                </div>

                {rubricErr && <ErrorState message={rubricErr} />}
                {rubricMsg && (
                  <p className="text-small text-success">{rubricMsg}</p>
                )}

                <div>
                  <Button
                    onClick={saveRubric}
                    disabled={updateRubric.isPending}
                  >
                    {updateRubric.isPending ? <Spinner /> : <Save size={18} />}
                    Guardar rúbrica
                  </Button>
                </div>
              </div>
            )}
          </Card>

          {/* Idioma de análisis */}
          <Card>
            <CardTitle className="mb-1">Idioma de análisis</CardTitle>
            <p className="mb-4 text-small text-text-secondary">
              Idioma usado para transcribir y analizar las próximas llamadas.
            </p>
            <div className="flex items-end gap-3">
              <div className="w-52">
                <Label htmlFor="lang">Idioma</Label>
                <Select
                  id="lang"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                >
                  {LANGUAGES.map((l) => (
                    <option key={l.code} value={l.code}>
                      {l.label}
                    </option>
                  ))}
                </Select>
              </div>
              <Button
                onClick={saveLanguage}
                disabled={updateSettings.isPending}
              >
                {updateSettings.isPending ? <Spinner /> : <Save size={18} />}
                Guardar
              </Button>
            </div>
            {settingsMsg && (
              <p className="mt-3 text-small text-success">{settingsMsg}</p>
            )}
          </Card>

          {/* Información del sistema */}
          {settings && (
            <Card>
              <CardTitle className="mb-3">Información del sistema</CardTitle>
              <dl className="flex flex-col gap-2 text-body">
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Proveedor de IA</dt>
                  <dd className="font-mono text-text-primary">
                    {settings.ai_provider}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-secondary">
                    Proveedor de transcripción
                  </dt>
                  <dd className="font-mono text-text-primary">
                    {settings.whisper_provider}
                  </dd>
                </div>
              </dl>
              <p className="mt-3 text-small text-text-muted">
                El proveedor de IA y transcripción se configura por variables
                de entorno en el backend.
              </p>
            </Card>
          )}
        </div>
      </main>
    </>
  );
}
