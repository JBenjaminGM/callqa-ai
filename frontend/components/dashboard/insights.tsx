'use client';

import Link from 'next/link';
import {
  AlertTriangle,
  Award,
  CheckCircle2,
  Clock,
  Gauge,
  MessageSquare,
  Mic,
  ShieldAlert,
  ShieldCheck,
  TrendingDown,
  Volume2,
} from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { PriorityBadge, ScoreBadge } from '@/components/ui/badge';
import { ScoreRadar } from '@/components/charts/score-radar';
import { dimensionLabel, formatDuration } from '@/lib/utils';
import type {
  AgentCampaignBreakdown,
  AgentPercentile,
  AgentRecommendationStat,
  CampaignKpi,
  ConversationMetrics,
  ConversationSummary,
  DashboardAlert,
  RecommendationStat,
} from '@/types';

const SEVERITY_DOT: Record<string, string> = {
  high: 'bg-danger',
  medium: 'bg-warning',
  low: 'bg-info',
};

/** Fila de alertas accionables del jefe. */
export function AlertsPanel({ alerts }: { alerts: DashboardAlert[] }) {
  if (alerts.length === 0) {
    return (
      <Card className="flex items-center gap-3">
        <CheckCircle2 size={20} className="text-success" />
        <span className="text-body text-text-secondary">
          Sin alertas en este periodo. El equipo está dentro de los umbrales.
        </span>
      </Card>
    );
  }

  return (
    <Card>
      <CardTitle className="mb-3 flex items-center gap-2">
        <AlertTriangle size={18} className="text-warning" />
        Alertas accionables
        <span className="rounded-full bg-warning/15 px-2 py-0.5 text-small font-semibold text-warning">
          {alerts.length}
        </span>
      </CardTitle>
      <ul className="flex flex-col divide-y divide-border">
        {alerts.map((a, i) => {
          const href = a.call_id
            ? `/calls/${a.call_id}`
            : a.agent_id
              ? `/agents/${a.agent_id}`
              : undefined;
          const body = (
            <div className="flex items-start gap-3 py-2.5">
              <span
                className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${
                  SEVERITY_DOT[a.severity] ?? 'bg-info'
                }`}
              />
              <div className="min-w-0">
                <p className="text-body font-medium text-text-primary">
                  {a.title}
                </p>
                <p className="text-small text-text-secondary">{a.description}</p>
              </div>
            </div>
          );
          return (
            <li key={i}>
              {href ? (
                <Link
                  href={href}
                  className="-mx-2 block rounded-lg px-2 transition-colors hover:bg-bg-accent/40"
                >
                  {body}
                </Link>
              ) : (
                body
              )}
            </li>
          );
        })}
      </ul>
    </Card>
  );
}

/** Tabla de KPIs por campaña con delta vs periodo anterior. */
export function CampaignKpiTable({ rows }: { rows: CampaignKpi[] }) {
  if (rows.length === 0) {
    return (
      <Card>
        <CardTitle className="mb-2">KPIs por campaña</CardTitle>
        <p className="text-small text-text-muted">Sin datos en este periodo.</p>
      </Card>
    );
  }
  return (
    <Card>
      <CardTitle className="mb-3">KPIs por campaña</CardTitle>
      <div className="overflow-x-auto">
        <table className="w-full text-small">
          <thead>
            <tr className="text-left text-text-muted">
              <th className="pb-2 pr-3 font-medium">Campaña</th>
              <th className="pb-2 pr-3 font-medium">Llamadas</th>
              <th className="pb-2 pr-3 font-medium">Score</th>
              <th className="pb-2 pr-3 font-medium">Δ</th>
              <th className="pb-2 pr-3 font-medium">% rojas</th>
              <th className="pb-2 pr-3 font-medium">Sentimiento</th>
              <th className="pb-2 font-medium">Duración</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.campaign} className="border-t border-border">
                <td className="py-2 pr-3 text-text-primary">{r.campaign}</td>
                <td className="py-2 pr-3 text-text-secondary">{r.total_calls}</td>
                <td className="py-2 pr-3">
                  <ScoreBadge score={Math.round(r.avg_score)} />
                </td>
                <td className="py-2 pr-3">
                  <DeltaCell delta={r.score_delta} />
                </td>
                <td className="py-2 pr-3 text-text-secondary">{r.red_pct}%</td>
                <td className="py-2 pr-3 text-text-secondary">
                  {r.sentiment ?? '—'}
                </td>
                <td className="py-2 text-text-secondary">
                  {formatDuration(r.avg_duration_seconds)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function DeltaCell({ delta }: { delta?: number | null }) {
  if (delta == null) return <span className="text-text-muted">—</span>;
  const positive = delta >= 0;
  return (
    <span
      className={positive ? 'font-medium text-success' : 'font-medium text-danger'}
    >
      {positive ? '↑' : '↓'} {Math.abs(delta).toFixed(1)}
    </span>
  );
}

/** Lista de problemas recurrentes (recomendaciones agregadas). */
export function TopProblems({
  items,
  title = 'Top problemas recurrentes',
}: {
  items: (RecommendationStat | AgentRecommendationStat)[];
  title?: string;
}) {
  if (items.length === 0) {
    return (
      <Card>
        <CardTitle className="mb-2">{title}</CardTitle>
        <p className="text-small text-text-muted">
          Sin recomendaciones registradas en este periodo.
        </p>
      </Card>
    );
  }
  return (
    <Card>
      <CardTitle className="mb-3">{title}</CardTitle>
      <ul className="flex flex-col gap-3">
        {items.map((it, i) => (
          <li
            key={i}
            className="rounded-lg border border-border bg-bg-secondary p-3"
          >
            <div className="mb-1 flex flex-wrap items-center gap-2">
              <PriorityBadge
                priority={(it.priority as 'high' | 'medium' | 'low') ?? 'medium'}
              />
              <span className="text-body font-semibold text-text-primary">
                {it.title}
              </span>
              <span className="rounded-full bg-accent-primary/10 px-2 py-0.5 text-small font-semibold text-accent-primary">
                ×{it.count}
              </span>
            </div>
            {it.sample_description && (
              <p className="text-small text-text-secondary">
                {it.sample_description}
              </p>
            )}
            {'evidence' in it && it.evidence && (
              <p className="mt-1.5 border-l-2 border-accent-primary/40 pl-2 text-small italic text-text-muted">
                «{it.evidence}»
              </p>
            )}
            <p className="mt-1 text-small text-text-muted">
              Dimensión: {dimensionLabel(it.dimension)}
            </p>
          </li>
        ))}
      </ul>
    </Card>
  );
}

/** Métricas agregadas de conversación del equipo. */
export function ConversationStats({
  summary,
}: {
  summary: ConversationSummary;
}) {
  const items = [
    {
      icon: <Mic size={16} />,
      label: 'Habla del agente',
      value: summary.avg_agent_talk_pct != null ? `${summary.avg_agent_talk_pct}%` : '—',
    },
    {
      icon: <Volume2 size={16} />,
      label: 'Silencio medio',
      value: summary.avg_silence_pct != null ? `${summary.avg_silence_pct}%` : '—',
    },
    {
      icon: <Gauge size={16} />,
      label: 'Ratio hablar/escuchar',
      value: summary.avg_talk_to_listen_ratio?.toFixed(2) ?? '—',
    },
    {
      icon: <MessageSquare size={16} />,
      label: 'Palabras/min (agente)',
      value: summary.avg_agent_words_per_minute?.toFixed(0) ?? '—',
    },
    {
      icon: <Clock size={16} />,
      label: 'Monólogo más largo',
      value: formatDuration(summary.avg_longest_monologue_seconds),
    },
  ];
  return (
    <Card>
      <CardTitle className="mb-3 flex items-center gap-2">
        <TrendingDown size={18} className="text-accent-primary" />
        Dinámica de conversación
        <span className="text-small font-normal text-text-muted">
          ({summary.calls_measured} llamadas)
        </span>
      </CardTitle>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {items.map((it) => (
          <div key={it.label} className="flex flex-col gap-1">
            <span className="flex items-center gap-1.5 text-small text-text-secondary">
              {it.icon}
              {it.label}
            </span>
            <span className="text-h3 text-text-primary">{it.value}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

/** Tarjeta de percentil anónimo del asesor dentro de su campaña. */
export function PercentileCard({ data }: { data: AgentPercentile }) {
  if (!data.available) {
    return (
      <Card className="flex items-center gap-3">
        <Award size={20} className="text-text-muted" />
        <span className="text-small text-text-secondary">
          Aún no hay suficientes asesores con datos en tu campaña para mostrar tu
          posición de forma anónima.
        </span>
      </Card>
    );
  }
  return (
    <Card className="flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <Award size={28} className="text-accent-primary" />
        <div>
          <p className="text-h3 text-text-primary">
            Percentil {data.percentile}
          </p>
          <p className="text-small text-text-secondary">
            Tu posición anónima en {data.campaign ?? 'tu campaña'} · puesto{' '}
            {data.rank} de {data.peers_count}
          </p>
        </div>
      </div>
      <div className="flex gap-6 text-center">
        <div>
          <p className="text-small text-text-secondary">Tu media</p>
          <p className="text-h3 text-text-primary">{data.agent_avg?.toFixed(1)}</p>
        </div>
        <div>
          <p className="text-small text-text-secondary">Media campaña</p>
          <p className="text-h3 text-text-muted">
            {data.campaign_avg?.toFixed(1)}
          </p>
        </div>
      </div>
    </Card>
  );
}

/** Desglose del asesor por campaña + cumplimiento de la nota de producto. */
export function AgentCampaignBreakdownList({
  items,
}: {
  items: AgentCampaignBreakdown[];
}) {
  if (items.length === 0) return null;
  return (
    <Card>
      <CardTitle className="mb-3">Mi desempeño por campaña</CardTitle>
      <div className="flex flex-col gap-3">
        {items.map((c) => (
          <div
            key={c.campaign}
            className="rounded-lg border border-border bg-bg-secondary p-3"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-body font-semibold text-text-primary">
                {c.campaign}
              </span>
              <span className="flex items-center gap-2">
                <span className="text-small text-text-muted">
                  {c.total_calls} llamadas
                </span>
                <ScoreBadge score={Math.round(c.avg_score)} />
              </span>
            </div>
            {c.compliance && (
              <div className="mt-2 flex flex-col gap-1.5 text-small">
                {c.compliance.coverage_pct != null && (
                  <span className="flex items-center gap-1.5 text-text-secondary">
                    <ShieldCheck size={14} className="text-success" />
                    Frases obligatorias cubiertas: {c.compliance.coverage_pct}%
                  </span>
                )}
                {c.compliance.prohibited_hits > 0 && (
                  <span className="flex items-center gap-1.5 text-danger">
                    <ShieldAlert size={14} />
                    {c.compliance.prohibited_hits} posible(s) afirmación(es)
                    prohibida(s)
                  </span>
                )}
                {c.compliance.mandatory_missing.length > 0 && (
                  <span className="text-text-muted">
                    Pendiente de mencionar:{' '}
                    {c.compliance.mandatory_missing.join(' · ')}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}

/** Tarjeta de métricas de conversación de una llamada concreta. */
export function ConversationMetricsCard({
  metrics,
}: {
  metrics: ConversationMetrics;
}) {
  const agentPct = metrics.agent_talk_pct ?? 0;
  const customerPct = metrics.customer_talk_pct ?? 0;
  const items = [
    {
      label: 'Ratio hablar/escuchar',
      value: metrics.talk_to_listen_ratio?.toFixed(2) ?? '—',
    },
    {
      label: 'Silencio / dead-air',
      value: metrics.silence_pct != null ? `${metrics.silence_pct}%` : '—',
    },
    {
      label: 'Monólogo más largo',
      value: formatDuration(metrics.longest_agent_monologue_seconds),
    },
    {
      label: 'Palabras/min (agente)',
      value: metrics.agent_words_per_minute?.toFixed(0) ?? '—',
    },
    {
      label: 'Turnos/min',
      value: metrics.turns_per_minute?.toFixed(1) ?? '—',
    },
  ];
  return (
    <Card>
      <CardTitle className="mb-3 flex items-center gap-2">
        <MessageSquare size={18} className="text-accent-primary" />
        Dinámica de la conversación
      </CardTitle>

      {/* Reparto de habla agente vs cliente */}
      <div className="mb-1 flex justify-between text-small text-text-secondary">
        <span>Ejecutivo {agentPct}%</span>
        <span>Cliente {customerPct}%</span>
      </div>
      <div className="mb-4 flex h-2.5 w-full overflow-hidden rounded-full bg-bg-accent">
        <div
          className="h-full bg-accent-primary"
          style={{ width: `${agentPct}%` }}
        />
        <div className="h-full bg-info" style={{ width: `${customerPct}%` }} />
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {items.map((it) => (
          <div key={it.label} className="flex flex-col gap-1">
            <span className="text-small text-text-secondary">{it.label}</span>
            <span className="text-h3 text-text-primary">{it.value}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

/** Radar de las dimensiones del equipo (puntos débiles). */
export function TeamRadar({ averages }: { averages: Record<string, number> }) {
  if (!averages || Object.keys(averages).length === 0) return null;
  return (
    <Card>
      <CardTitle className="mb-2">Dimensiones del equipo</CardTitle>
      <ScoreRadar scores={averages} seriesLabel="Equipo" />
    </Card>
  );
}
