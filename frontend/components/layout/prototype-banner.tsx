import { AlertTriangle } from 'lucide-react';

/**
 * Banner persistente de aviso de prototipo (requisito Minsait/Indra,
 * documento de visión sección 7.5).
 */
export function PrototypeBanner() {
  return (
    <div
      className="flex items-center justify-center gap-2 bg-warning/15 px-4 py-1.5
                 text-small font-medium text-warning"
      role="alert"
    >
      <AlertTriangle size={14} />
      <span>
        PROTOTIPO — DEMO INTERNA. No utilizar con datos reales de clientes sin
        aprobación de Compliance.
      </span>
    </div>
  );
}
