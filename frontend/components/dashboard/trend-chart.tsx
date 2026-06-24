'use client';

import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Card, CardTitle } from '@/components/ui/card';
import { BrandTooltip } from '@/components/dashboard/viz';

function shortDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: 'short' });
}

/**
 * Evolución del volumen de llamadas + score medio diario, con línea de meta.
 * Área con gradiente (volumen, eje izq.) + línea (score, eje der. 0-100).
 */
export function CallsTrendChart({
  data,
  target,
}: {
  data: { date: string; count: number; avg_score?: number | null }[];
  target?: number;
}) {
  const chartData = data.map((d) => ({
    ...d,
    label: shortDate(d.date),
    avg_score: d.avg_score ?? null,
  }));
  return (
    <Card>
      <CardTitle className="mb-4">evolución de <span className="hl">llamadas</span> y score</CardTitle>
      <ResponsiveContainer width="100%" height={260}>
        <ComposedChart data={chartData} margin={{ top: 6, right: 8, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="volGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent-primary)" stopOpacity={0.35} />
              <stop offset="100%" stopColor="var(--accent-primary)" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            minTickGap={20}
          />
          <YAxis
            yAxisId="left"
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            domain={[0, 100]}
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={28}
          />
          <Tooltip
            content={
              <BrandTooltip
                formatter={(v, name) => (name === 'Score medio' ? `${v}` : `${v}`)}
              />
            }
          />
          {target != null && (
            <ReferenceLine
              yAxisId="right"
              y={target}
              stroke="var(--success)"
              strokeDasharray="4 4"
              strokeOpacity={0.7}
              label={{ value: `meta ${target}`, position: 'right', fill: 'var(--success)', fontSize: 10 }}
            />
          )}
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="count"
            name="Llamadas"
            stroke="var(--accent-primary)"
            strokeWidth={2}
            fill="url(#volGrad)"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="avg_score"
            name="Score medio"
            stroke="var(--fucsia)"
            strokeWidth={2.5}
            dot={false}
            connectNulls
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Card>
  );
}
