import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { DeltaPill, MiniProgress, Sparkline } from '@/components/dashboard/viz';

/**
 * KPI card premium: eyebrow + valor grande (tabular), variación vs periodo
 * anterior, y opcionalmente un sparkline o una barra de progreso a objetivo.
 */
export function StatCard({
  label,
  value,
  unit,
  icon,
  accent = 'var(--accent-primary)',
  delta,
  deltaSuffix,
  deltaNeutralIsGood = true,
  caption,
  sparkData,
  target,
  className,
}: {
  label: string;
  value: string | number;
  unit?: string;
  icon?: React.ReactNode;
  accent?: string;
  delta?: number | null;
  deltaSuffix?: string;
  deltaNeutralIsGood?: boolean;
  caption?: string;
  sparkData?: number[];
  target?: { value: number; label?: string };
  className?: string;
}) {
  return (
    <Card className={cn('flex flex-col justify-between gap-3', className)}>
      <div className="flex items-start justify-between">
        <span className="destacado text-[11px] text-text-muted">{label}</span>
        {icon && (
          <span
            className="flex h-8 w-8 items-center justify-center rounded-lg"
            style={{ background: 'var(--bg-accent)', color: accent }}
          >
            {icon}
          </span>
        )}
      </div>

      <div className="flex items-end gap-2">
        <span
          className="font-black leading-none tabular-nums"
          style={{ color: accent, fontSize: 34 }}
        >
          {value}
        </span>
        {unit && (
          <span className="mb-0.5 text-body text-text-muted">{unit}</span>
        )}
      </div>

      {(delta != null || caption) && (
        <div className="flex items-center gap-2">
          {delta != null && (
            <DeltaPill
              delta={delta}
              suffix={deltaSuffix}
              neutralIsGood={deltaNeutralIsGood}
            />
          )}
          {caption && (
            <span className="text-small text-text-muted">{caption}</span>
          )}
        </div>
      )}

      {target && (
        <div className="flex flex-col gap-1">
          <MiniProgress
            value={typeof value === 'number' ? value : Number(value) || 0}
            color={accent}
          />
          <span className="text-[11px] text-text-muted">
            {target.label ?? `Meta: ${target.value}`}
          </span>
        </div>
      )}

      {sparkData && sparkData.length > 1 && (
        <Sparkline data={sparkData} color={accent} width={220} height={34} />
      )}
    </Card>
  );
}
