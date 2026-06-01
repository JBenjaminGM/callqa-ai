import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

/** Tarjeta de KPI del dashboard (label, valor grande y delta opcional). */
export function KpiCard({
  label,
  value,
  delta,
  icon,
}: {
  label: string;
  value: string | number;
  delta?: string;
  icon?: React.ReactNode;
}) {
  const deltaPositive = delta ? !delta.trim().startsWith('-') : true;

  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <p className="text-small text-text-secondary">{label}</p>
        {icon && <span className="text-accent-primary">{icon}</span>}
      </div>
      <p className="text-kpi text-accent-primary">{value}</p>
      {delta && (
        <p
          className={cn(
            'text-small font-medium',
            deltaPositive ? 'text-success' : 'text-danger',
          )}
        >
          {deltaPositive ? '↑' : '↓'} {delta} vs. periodo anterior
        </p>
      )}
    </Card>
  );
}
