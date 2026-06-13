'use client';

import { Input, Textarea } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import type { Campaign, CampaignDraft } from '@/types';

/** Estado del formulario: todos los campos como strings (las listas, multilínea). */
export interface CampaignFormState {
  name: string;
  product_service: string;
  offer_description: string;
  key_benefits: string;
  pricing_conditions: string;
  customer_requirements: string;
  mandatory_phrases: string;
  prohibited_claims: string;
  target_audience: string;
  additional_notes: string;
}

type FieldKind = 'text' | 'textarea' | 'list';

interface FieldDef {
  key: keyof CampaignFormState;
  label: string;
  kind: FieldKind;
  placeholder?: string;
  hint?: string;
}

/** Definición y orden de los campos de la nota de producto. */
export const CAMPAIGN_FIELDS: FieldDef[] = [
  { key: 'name', label: 'Nombre de la campaña *', kind: 'text', placeholder: 'Ej. Tarjeta Oro 2026' },
  { key: 'product_service', label: 'Producto / servicio', kind: 'text', placeholder: 'Ej. Tarjeta de crédito Oro' },
  {
    key: 'offer_description',
    label: 'Descripción de la oferta',
    kind: 'textarea',
    placeholder: 'En qué consiste la oferta y qué se le propone al cliente…',
  },
  { key: 'key_benefits', label: 'Beneficios clave', kind: 'list', hint: 'Un beneficio por línea.' },
  {
    key: 'pricing_conditions',
    label: 'Precio y condiciones',
    kind: 'textarea',
    placeholder: 'TEA, comisiones, plazos, condiciones económicas…',
  },
  {
    key: 'customer_requirements',
    label: 'Requisitos del cliente',
    kind: 'textarea',
    placeholder: 'Requisitos que debe cumplir el cliente para acceder a la oferta…',
  },
  {
    key: 'mandatory_phrases',
    label: 'Frases / script obligatorio',
    kind: 'list',
    hint: 'Una frase por línea — lo que el ejecutivo DEBE mencionar.',
  },
  {
    key: 'prohibited_claims',
    label: 'Afirmaciones prohibidas',
    kind: 'list',
    hint: 'Una por línea — lo que el ejecutivo NO debe decir.',
  },
  { key: 'target_audience', label: 'Público objetivo', kind: 'text', placeholder: 'A quién va dirigida la campaña' },
  { key: 'additional_notes', label: 'Notas adicionales', kind: 'textarea' },
];

const LIST_KEYS = ['key_benefits', 'mandatory_phrases', 'prohibited_claims'] as const;

export function emptyCampaignForm(): CampaignFormState {
  return {
    name: '',
    product_service: '',
    offer_description: '',
    key_benefits: '',
    pricing_conditions: '',
    customer_requirements: '',
    mandatory_phrases: '',
    prohibited_claims: '',
    target_audience: '',
    additional_notes: '',
  };
}

function listToText(v?: string[] | null): string {
  return (v ?? []).join('\n');
}

function textToList(v: string): string[] {
  return v
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);
}

/** Carga completa de una campaña existente en el formulario (incluye vacíos). */
export function campaignToForm(c: Campaign): CampaignFormState {
  return {
    name: c.name ?? '',
    product_service: c.product_service ?? '',
    offer_description: c.offer_description ?? '',
    key_benefits: listToText(c.key_benefits),
    pricing_conditions: c.pricing_conditions ?? '',
    customer_requirements: c.customer_requirements ?? '',
    mandatory_phrases: listToText(c.mandatory_phrases),
    prohibited_claims: listToText(c.prohibited_claims),
    target_audience: c.target_audience ?? '',
    additional_notes: c.additional_notes ?? '',
  };
}

/**
 * Fusiona un borrador (de IA o PDF) sobre el estado actual, SIN pisar lo que el
 * usuario ya escribió: solo rellena los campos que el borrador trae con valor.
 */
export function mergeDraftIntoForm(
  draft: CampaignDraft,
  base: CampaignFormState,
): CampaignFormState {
  const f = { ...base };
  const setText = (k: keyof CampaignFormState, val?: string | null) => {
    if (val != null && val !== '' && !f[k]) f[k] = val;
  };
  setText('name', draft.name);
  setText('product_service', draft.product_service);
  setText('offer_description', draft.offer_description);
  setText('pricing_conditions', draft.pricing_conditions);
  setText('customer_requirements', draft.customer_requirements);
  setText('target_audience', draft.target_audience);
  setText('additional_notes', draft.additional_notes);
  for (const k of LIST_KEYS) {
    const arr = draft[k];
    if (arr && arr.length && !f[k]) f[k] = listToText(arr);
  }
  return f;
}

/** Convierte el estado del formulario al payload de la API. */
export function formToPayload(s: CampaignFormState) {
  const t = (v: string) => {
    const x = v.trim();
    return x ? x : null;
  };
  return {
    name: s.name.trim(),
    product_service: t(s.product_service),
    offer_description: t(s.offer_description),
    key_benefits: textToList(s.key_benefits),
    pricing_conditions: t(s.pricing_conditions),
    customer_requirements: t(s.customer_requirements),
    mandatory_phrases: textToList(s.mandatory_phrases),
    prohibited_claims: textToList(s.prohibited_claims),
    target_audience: t(s.target_audience),
    additional_notes: t(s.additional_notes),
  };
}

/** Forma de "borrador" del estado actual (para enviar como contexto a la IA). */
export function formToDraft(s: CampaignFormState): CampaignDraft {
  return formToPayload(s);
}

/** Campos editables de la nota de producto (componente controlado). */
export function CampaignFields({
  value,
  onChange,
  highlight = [],
}: {
  value: CampaignFormState;
  onChange: (next: CampaignFormState) => void;
  highlight?: string[];
}) {
  const set = (k: keyof CampaignFormState, v: string) =>
    onChange({ ...value, [k]: v });

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {CAMPAIGN_FIELDS.map((f) => {
        const flagged = highlight.includes(f.key);
        const wide = f.kind !== 'text';
        return (
          <div key={f.key} className={cn(wide && 'sm:col-span-2')}>
            <Label htmlFor={f.key}>
              {f.label}
              {flagged && (
                <span className="ml-2 rounded bg-warning/15 px-1.5 py-0.5 text-small text-warning">
                  Completar
                </span>
              )}
            </Label>
            {f.kind === 'text' ? (
              <Input
                id={f.key}
                value={value[f.key]}
                placeholder={f.placeholder}
                onChange={(e) => set(f.key, e.target.value)}
                className={cn(flagged && 'border-warning')}
              />
            ) : (
              <Textarea
                id={f.key}
                rows={f.kind === 'list' ? 4 : 3}
                value={value[f.key]}
                placeholder={f.placeholder}
                onChange={(e) => set(f.key, e.target.value)}
                className={cn(flagged && 'border-warning')}
              />
            )}
            {f.hint && <p className="mt-1 text-small text-text-muted">{f.hint}</p>}
          </div>
        );
      })}
    </div>
  );
}
