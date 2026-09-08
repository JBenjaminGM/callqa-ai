import { cn } from '@/lib/utils';
import { scoreLevel, scoreLabel, STATUS_LABELS } from '@/lib/utils';
import type { CallStatus } from '@/types';

/** Badge de score con color semántico (verde/amarillo/rojo). */
export function ScoreBadge({
  score,
  showLabel = false,
}: {
  score: number;
  showLabel?: boolean;
}) {
  const level = scoreLevel(score);
  const colorClass = {
    success: 'bg-success/15 text-success',
    warning: 'bg-warning/15 text-warning',
    danger: 'bg-danger/15 text-danger',
  }[level];

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-control px-2.5 py-1',
        'text-small font-mono font-semibold tabular-nums',
        colorClass,
      )}
    >
      <span className="h-2 w-2 rounded-full bg-current" />
      {score}
      {showLabel && <span className="font-normal">· {scoreLabel(score)}</span>}
    </span>
  );
}

const STATUS_STYLES: Record<CallStatus, string> = {
  QUEUED: 'bg-info/15 text-info',
  TRANSCRIBING: 'bg-info/15 text-info',
  ANALYZING: 'bg-warning/15 text-warning',
  DONE: 'bg-success/15 text-success',
  ERROR: 'bg-danger/15 text-danger',
};

/** Badge del estado de procesamiento de una llamada. */
export function StatusBadge({ status }: { status: CallStatus }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-control px-2.5 py-1',
        'text-small font-medium',
        STATUS_STYLES[status],
      )}
    >
      <span
        className={cn(
          'h-2 w-2 rounded-full bg-current',
          (status === 'TRANSCRIBING' || status === 'ANALYZING') &&
            'animate-pulse',
        )}
      />
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}

/** Badge de prioridad de una recomendación. */
export function PriorityBadge({
  priority,
}: {
  priority: 'high' | 'medium' | 'low';
}) {
  const styles = {
    high: 'bg-danger/15 text-danger',
    medium: 'bg-warning/15 text-warning',
    low: 'bg-info/15 text-info',
  }[priority];
  const label = { high: 'Alta', medium: 'Media', low: 'Baja' }[priority];
  return (
    <span
      className={cn(
        'rounded-control px-2 py-0.5 text-small font-semibold',
        styles,
      )}
    >
      {label}
    </span>
  );
}
