'use client';

import { useEffect, useState } from 'react';
import { Plus, Save, Trash2 } from 'lucide-react';
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
import type { RubricDimensionInput } from '@/types';

const LANGUAGES = [
  { code: 'es', label: 'Español' },
  { code: 'en', label: 'Inglés' },
  { code: 'pt', label: 'Portugués' },
  { code: 'fr', label: 'Francés' },
];

/** Umbrales de QA configurables (coinciden con app_settings del backend). */
const QA_FIELDS = [
  {
    key: 'qa_target_score',
    label: 'Meta de score (verde)',
    hint: 'A partir de aquí se considera excelente.',
    min: 0,
    max: 100,
  },
  {
    key: 'qa_low_agent_threshold',
    label: 'Asesor «requiere atención» por debajo de',
    hint: 'Dispara alertas de bajo rendimiento.',
    min: 0,
    max: 100,
  },
  {
    key: 'qa_red_call_threshold',
    label: 'Llamada en banda roja por debajo de',
    hint: 'Marca las llamadas críticas.',
    min: 0,
    max: 100,
  },
  {
    key: 'qa_min_calls_ranking',
    label: 'Mínimo de llamadas para rankings',
    hint: 'Evita rankings con muestras muy pequeñas.',
    min: 1,
    max: 1000,
  },
  {
    key: 'qa_trend_drop_alert',
    label: 'Caída de score que dispara alerta (puntos)',
    hint: 'Detecta tendencias negativas.',
    min: 0,
    max: 100,
  },
] as const;

/** Página de configuración: rúbrica de evaluación (con subcategorías) e idioma. */
export default function SettingsPage() {
  const { data: rubric, isLoading: rubricLoading, error: rubricError } =
    useRubric();
  const { data: settings } = useSettings();
  const updateRubric = useUpdateRubric();
  const updateSettings = useUpdateSettings();

  // Estado local editable: la rúbrica completa (categorías + subcategorías).
  const [dims, setDims] = useState<RubricDimensionInput[]>([]);
  const [language, setLanguage] = useState('es');
  const [rubricMsg, setRubricMsg] = useState<string | null>(null);
  const [rubricErr, setRubricErr] = useState<string | null>(null);
  const [settingsMsg, setSettingsMsg] = useState<string | null>(null);

  // Umbrales / metas de QA configurables.
  const [qa, setQa] = useState<Record<string, number>>({});
  const [qaMsg, setQaMsg] = useState<string | null>(null);

  useEffect(() => {
    if (rubric) {
      setDims(
        rubric.map((d) => ({
          dimension_key: d.dimension_key,
          dimension_name: d.dimension_name,
          description: d.description ?? '',
          weight: Number(d.weight),
          criteria: (d.criteria ?? []).map((c) => ({
            name: c.name,
            enabled: c.enabled,
          })),
        })),
      );
    }
  }, [rubric]);

  useEffect(() => {
    if (settings) {
      setLanguage(settings.default_language);
      setQa({
        qa_target_score: settings.qa_target_score ?? 90,
        qa_low_agent_threshold: settings.qa_low_agent_threshold ?? 80,
        qa_red_call_threshold: settings.qa_red_call_threshold ?? 60,
        qa_min_calls_ranking: settings.qa_min_calls_ranking ?? 5,
        qa_trend_drop_alert: settings.qa_trend_drop_alert ?? 5,
      });
    }
  }, [settings]);

  const total = dims.reduce((a, d) => a + (Number(d.weight) || 0), 0);

  // --- Helpers de edición ---
  function patchDim(i: number, patch: Partial<RubricDimensionInput>) {
    setDims((ds) => ds.map((d, j) => (j === i ? { ...d, ...patch } : d)));
  }
  function patchCriterion(
    i: number,
    ci: number,
    patch: Partial<{ name: string; enabled: boolean }>,
  ) {
    setDims((ds) =>
      ds.map((d, j) =>
        j === i
          ? {
              ...d,
              criteria: d.criteria.map((c, k) =>
                k === ci ? { ...c, ...patch } : c,
              ),
            }
          : d,
      ),
    );
  }
  function addCriterion(i: number) {
    setDims((ds) =>
      ds.map((d, j) =>
        j === i
          ? { ...d, criteria: [...d.criteria, { name: '', enabled: true }] }
          : d,
      ),
    );
  }
  function removeCriterion(i: number, ci: number) {
    setDims((ds) =>
      ds.map((d, j) =>
        j === i
          ? { ...d, criteria: d.criteria.filter((_, k) => k !== ci) }
          : d,
      ),
    );
  }
  function addDimension() {
    setDims((ds) => [
      ...ds,
      { dimension_name: '', description: '', weight: 0, criteria: [] },
    ]);
  }
  function removeDimension(i: number) {
    setDims((ds) => ds.filter((_, j) => j !== i));
  }

  async function saveRubric() {
    setRubricMsg(null);
    setRubricErr(null);
    if (dims.some((d) => !d.dimension_name.trim())) {
      setRubricErr('Todas las categorías deben tener nombre.');
      return;
    }
    if (Math.abs(total - 100) > 0.5) {
      setRubricErr(
        `Los pesos deben sumar 100%. Suma actual: ${total.toFixed(2)}%.`,
      );
      return;
    }
    const payload: RubricDimensionInput[] = dims.map((d) => ({
      dimension_key: d.dimension_key,
      dimension_name: d.dimension_name.trim(),
      description: d.description?.trim() || null,
      weight: Number(d.weight) || 0,
      criteria: d.criteria
        .filter((c) => c.name.trim())
        .map((c) => ({ name: c.name.trim(), enabled: c.enabled })),
    }));
    try {
      await updateRubric.mutateAsync(payload);
      setRubricMsg('Rúbrica actualizada. Aplica a las próximas llamadas.');
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

  async function saveThresholds() {
    setQaMsg(null);
    try {
      await updateSettings.mutateAsync(qa);
      setQaMsg('Umbrales de QA actualizados.');
    } catch (err) {
      setQaMsg(getErrorMessage(err));
    }
  }

  return (
    <>
      <Header title="Configuración" />
      <main className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-6">
          {/* Rúbrica */}
          <Card>
            <CardTitle className="mb-1">Rúbrica de evaluación</CardTitle>
            <p className="mb-4 text-small text-text-secondary">
              Define las categorías (con su peso %) y las subcategorías que la IA
              tendrá en cuenta. Activa/desactiva subcategorías, añade las tuyas o
              crea categorías nuevas. La suma de pesos debe ser 100%.
            </p>

            {rubricLoading && (
              <div className="flex flex-col gap-2">
                {[0, 1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-20" />
                ))}
              </div>
            )}
            {rubricError && <ErrorState message={getErrorMessage(rubricError)} />}

            {!rubricLoading && (
              <div className="flex flex-col gap-4">
                {dims.map((dim, i) => (
                  <div
                    key={dim.dimension_key ?? `new-${i}`}
                    className="rounded-lg border border-border bg-bg-secondary p-3"
                  >
                    {/* Cabecera: nombre + peso + eliminar */}
                    <div className="mb-2 flex items-center gap-2">
                      <Input
                        value={dim.dimension_name}
                        placeholder="Nombre de la categoría"
                        onChange={(e) =>
                          patchDim(i, { dimension_name: e.target.value })
                        }
                        className="flex-1 font-semibold"
                      />
                      <div className="flex w-24 items-center gap-1">
                        <Input
                          type="number"
                          min={0}
                          max={100}
                          step="0.01"
                          value={dim.weight}
                          onChange={(e) =>
                            patchDim(i, { weight: Number(e.target.value) })
                          }
                        />
                        <span className="text-small text-text-muted">%</span>
                      </div>
                      <button
                        onClick={() => removeDimension(i)}
                        title="Eliminar categoría"
                        className="rounded-md p-2 text-text-muted transition-colors hover:bg-danger/10 hover:text-danger"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>

                    {/* Subcategorías */}
                    <div className="flex flex-col gap-1.5 pl-1">
                      {dim.criteria.map((c, ci) => (
                        <div key={ci} className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={c.enabled}
                            onChange={(e) =>
                              patchCriterion(i, ci, { enabled: e.target.checked })
                            }
                            className="accent-[var(--accent-primary)]"
                            title={c.enabled ? 'Activa' : 'Inactiva'}
                          />
                          <Input
                            value={c.name}
                            placeholder="Subcategoría a evaluar"
                            onChange={(e) =>
                              patchCriterion(i, ci, { name: e.target.value })
                            }
                            className={
                              c.enabled
                                ? 'flex-1 !py-1.5 text-small'
                                : 'flex-1 !py-1.5 text-small line-through opacity-60'
                            }
                          />
                          <button
                            onClick={() => removeCriterion(i, ci)}
                            title="Quitar subcategoría"
                            className="rounded-md p-1.5 text-text-muted transition-colors hover:bg-danger/10 hover:text-danger"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      ))}
                      <button
                        onClick={() => addCriterion(i)}
                        className="mt-1 flex w-fit items-center gap-1 text-small text-accent-primary transition-opacity hover:opacity-80"
                      >
                        <Plus size={14} />
                        Añadir subcategoría
                      </button>
                    </div>
                  </div>
                ))}

                <Button variant="secondary" onClick={addDimension}>
                  <Plus size={18} />
                  Añadir categoría
                </Button>

                <div className="flex items-center justify-between border-t border-border pt-3">
                  <span className="text-body font-semibold text-text-primary">
                    Total de pesos
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
                  <Button onClick={saveRubric} disabled={updateRubric.isPending}>
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
              <Button onClick={saveLanguage} disabled={updateSettings.isPending}>
                {updateSettings.isPending ? <Spinner /> : <Save size={18} />}
                Guardar
              </Button>
            </div>
            {settingsMsg && (
              <p className="mt-3 text-small text-success">{settingsMsg}</p>
            )}
          </Card>

          {/* Umbrales / metas de QA */}
          <Card>
            <CardTitle className="mb-1">Umbrales de calidad (QA)</CardTitle>
            <p className="mb-4 text-small text-text-secondary">
              Definen los colores, las alertas y los rankings del dashboard. Se
              aplican de inmediato a toda la analítica.
            </p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {QA_FIELDS.map((f) => (
                <div key={f.key}>
                  <Label htmlFor={f.key}>{f.label}</Label>
                  <Input
                    id={f.key}
                    type="number"
                    min={f.min}
                    max={f.max}
                    value={qa[f.key] ?? ''}
                    onChange={(e) =>
                      setQa((q) => ({ ...q, [f.key]: Number(e.target.value) }))
                    }
                  />
                  <p className="mt-1 text-small text-text-muted">{f.hint}</p>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Button onClick={saveThresholds} disabled={updateSettings.isPending}>
                {updateSettings.isPending ? <Spinner /> : <Save size={18} />}
                Guardar umbrales
              </Button>
            </div>
            {qaMsg && <p className="mt-3 text-small text-success">{qaMsg}</p>}
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
                El proveedor de IA y transcripción se configura por variables de
                entorno en el backend.
              </p>
            </Card>
          )}
        </div>
      </main>
    </>
  );
}
