import { AlertTriangle } from 'lucide-react';

/**
 * Banner persistente de aviso de entorno de evaluación (requisito Minsait/Indra).
 * Estilo de marca: barra Pruno Oscuro con texto blanco y acento Fucsia.
 */
export function PrototypeBanner() {
  return (
    <div
      className="flex items-center justify-center gap-2 bg-[var(--pruno-oscuro)]
                 px-4 py-1.5 text-small font-medium text-white"
      role="alert"
    >
      <AlertTriangle size={14} className="text-[var(--fucsia)]" />
      <span>
        <span className="destacado text-[var(--fucsia)]">Vista previa</span> —
        entorno de evaluación. No utilizar con datos reales de clientes sin la
        aprobación previa de Compliance.
      </span>
    </div>
  );
}
