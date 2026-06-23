'use client';

import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { dimensionLabel } from '@/lib/utils';

/**
 * Gráfico radar de las 7 dimensiones.
 *
 * Compara los scores de una llamada/ejecutivo contra el promedio del equipo.
 */
export function ScoreRadar({
  scores,
  teamScores,
  seriesLabel = 'Esta llamada',
}: {
  scores: Record<string, number>;
  teamScores?: Record<string, number> | null;
  seriesLabel?: string;
}) {
  const data = Object.keys(scores).map((key) => ({
    dimension: dimensionLabel(key),
    score: scores[key],
    team: teamScores?.[key] ?? null,
  }));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={data} outerRadius="70%">
        <PolarGrid stroke="var(--border)" />
        <PolarAngleAxis
          dataKey="dimension"
          tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
        />
        <Radar
          name={seriesLabel}
          dataKey="score"
          stroke="var(--accent-primary)"
          fill="var(--accent-primary)"
          fillOpacity={0.3}
        />
        {teamScores && (
          <Radar
            name="Promedio equipo"
            dataKey="team"
            stroke="var(--info)"
            fill="var(--info)"
            fillOpacity={0.1}
          />
        )}
        <Legend wrapperStyle={{ fontSize: 12 }} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
