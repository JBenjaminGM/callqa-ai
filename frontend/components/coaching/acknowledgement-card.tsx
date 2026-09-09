'use client';

import { useState } from 'react';
import { Check, MessageSquare, Reply, Send } from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/input';
import { ErrorState, Spinner } from '@/components/ui/feedback';
import { getErrorMessage } from '@/lib/api';
import { isManager, useAuthStore } from '@/lib/auth';
import { useReplyAcknowledgement, useSaveAcknowledgement } from '@/lib/queries';
import { formatDateTime } from '@/lib/utils';
import type { CallDetail } from '@/types';

/**
 * La conversación sobre una evaluación, en el detalle de la llamada.
 *
 * Hasta aquí el asesor veía su nota y no podía hacer nada con ella. Ahora puede
 * darla por leída, explicarse y —si no está de acuerdo— pedir que la revise su
 * jefe, que contesta en el mismo sitio. Eso es lo que cierra el ciclo.
 *
 * Quién ve qué:
 * - el asesor dueño de la llamada responde y puede pedir revisión;
 * - el jefe lee lo que dijo y contesta;
 * - un jefe sin nada que leer no ve la tarjeta: no es asunto suyo hasta que
 *   el asesor escriba.
 */
export function AcknowledgementCard({ call }: { call: CallDetail }) {
  const user = useAuthStore((s) => s.user);
  const ack = call.acknowledgement ?? null;
  const esManager = isManager(user);
  // El asesor evaluado es el único que puede firmar el acuse.
  const esElEvaluado =
    !esManager && user?.agent_id != null && user.agent_id === call.agent?.id;

  if (!call.analysis) return null;
  if (!ack && !esElEvaluado) return null;

  return (
    <Card className={ack?.pending_review ? 'ring-1 ring-warning/40' : undefined}>
      <CardTitle className="mb-1 flex items-center gap-2">
        <MessageSquare size={18} className="text-accent-primary" />
        {esElEvaluado ? 'Tu respuesta a esta evaluación' : 'Respuesta del asesor'}
        {ack?.pending_review && (
          <span
            className="rounded-control bg-warning/15 px-2 py-0.5 text-[11px]
                       font-medium text-warning"
          >
            Revisión pendiente
          </span>
        )}
      </CardTitle>

      {ack && <Conversacion ack={ack} />}

      {esElEvaluado && <FormularioAsesor call={call} />}

      {esManager && ack && !ack.manager_reply && <FormularioJefe call={call} />}
    </Card>
  );
}

/* ----------------------------- La conversación ---------------------------- */

function Conversacion({ ack }: { ack: NonNullable<CallDetail['acknowledgement']> }) {
  return (
    <div className="mb-4 mt-3 flex flex-col gap-3">
      <div className="rounded-card border border-border bg-bg-secondary p-3">
        <p className="destacado mb-1 text-[11px] text-text-muted">
          {ack.user_name ?? 'El asesor'} ·{' '}
          {formatDateTime(ack.updated_at ?? ack.created_at)}
        </p>
        <p className="text-body text-text-secondary">
          {ack.comment?.trim() || 'Evaluación recibida, sin comentarios.'}
        </p>
        {ack.review_requested && (
          <p className="mt-2 flex items-center gap-1.5 text-small font-medium text-warning">
            <Reply size={14} />
            Pidió revisión de la nota.
          </p>
        )}
      </div>

      {ack.manager_reply && (
        <div className="rounded-card border border-accent-primary/30 bg-bg-secondary p-3">
          <p className="destacado mb-1 text-[11px] text-text-muted">
            {ack.replied_by_name ?? 'Jefe de área'} ·{' '}
            {ack.replied_at ? formatDateTime(ack.replied_at) : ''}
          </p>
          <p className="text-body text-text-secondary">{ack.manager_reply}</p>
        </div>
      )}
    </div>
  );
}

/* --------------------------- Formulario del asesor ------------------------- */

function FormularioAsesor({ call }: { call: CallDetail }) {
  const ack = call.acknowledgement ?? null;
  const save = useSaveAcknowledgement();
  const [abierto, setAbierto] = useState(!ack);
  const [comment, setComment] = useState(ack?.comment ?? '');
  const [pedirRevision, setPedirRevision] = useState(
    ack?.review_requested ?? false,
  );

  async function guardar() {
    await save.mutateAsync({
      callId: call.id,
      comment: comment.trim() || null,
      review_requested: pedirRevision,
    });
    setAbierto(false);
  }

  if (!abierto) {
    return (
      <Button variant="secondary" size="sm" onClick={() => setAbierto(true)}>
        <MessageSquare size={16} />
        Editar mi respuesta
      </Button>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {!ack && (
        <p className="text-small text-text-secondary">
          Da por leída la evaluación. Si quieres, cuenta tu versión de la
          llamada; y si crees que la nota no es justa, pide que la revise tu
          jefe de área.
        </p>
      )}

      <Textarea
        rows={3}
        value={comment}
        disabled={save.isPending}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Tu comentario sobre esta llamada (opcional)."
        aria-label="Tu comentario"
      />

      <label className="flex items-center gap-2 text-small text-text-secondary">
        <input
          type="checkbox"
          checked={pedirRevision}
          disabled={save.isPending}
          onChange={(e) => setPedirRevision(e.target.checked)}
          className="accent-[var(--accent-primary)]"
        />
        Pedir que un jefe revise esta nota
      </label>

      {save.isError && <ErrorState message={getErrorMessage(save.error)} />}

      <div className="flex items-center gap-3">
        <Button onClick={guardar} disabled={save.isPending}>
          {save.isPending ? <Spinner /> : <Check size={16} />}
          {ack ? 'Guardar' : 'Acusar recibo'}
        </Button>
        {ack && (
          <Button
            variant="ghost"
            onClick={() => setAbierto(false)}
            disabled={save.isPending}
          >
            Cancelar
          </Button>
        )}
      </div>
    </div>
  );
}

/* ---------------------------- Formulario del jefe -------------------------- */

function FormularioJefe({ call }: { call: CallDetail }) {
  const reply = useReplyAcknowledgement();
  const [texto, setTexto] = useState('');

  return (
    <div className="flex flex-col gap-3">
      <Textarea
        rows={3}
        value={texto}
        disabled={reply.isPending}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Responde al asesor: qué has revisado y en qué queda."
        aria-label="Respuesta al asesor"
      />

      {reply.isError && <ErrorState message={getErrorMessage(reply.error)} />}

      <div>
        <Button
          onClick={() =>
            reply.mutateAsync({ callId: call.id, reply: texto.trim() })
          }
          disabled={reply.isPending || !texto.trim()}
        >
          {reply.isPending ? <Spinner /> : <Send size={16} />}
          Responder
        </Button>
      </div>
    </div>
  );
}
