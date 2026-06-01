'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Phone, Star, TrendingUp, X } from 'lucide-react';
import { useAgents, useCampaigns, useDashboardSummary } from '@/lib/queries';
import { getErrorMessage } from '@/lib/api';
import { Header } from '@/components/layout/header';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { KpiCard } from '@/components/dashboard/kpi-card';
import { ScoreBadge } from '@/components/ui/badge';
import { EmptyState, ErrorState, Skeleton } from '@/components/ui/feedback';
import type { AgentScore } from '@/types';

const DISTRIBUTION_COLORS: Record<string, string> = {
  '0-59': 'var(--danger)',
  '60-79': 'var(--warning)',
  '80-100': 'var(--success)',
};

/** Dashboard principal con KPIs agregados del equipo. */
export default function DashboardPage() {
  const [period, setPeriod] = useState('30d');
  const [campaign, setCampaign] = useState('');
  const [agentId, setAgentId] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const { data: agents } = useAgents();
  const { data: campaigns } = useCampaigns();
  const { data, isLoading, error } = useDashboardSummary({
    period,
    campaign: campaign || undefined,
    agent_id: agentId ? Number(agentId) : undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
  });

  const hasFilters = Boolean(campaign || agentId || dateFrom || dateTo);
  function clearFilters() {
    setCampaign('');
    setAgentId('');
    setDateFrom('');
    setDateTo('');
    setPeriod('30d');
  }

  return (
    <>
      <Header title="Dashboard" />
      <main className="flex-1 overflow-y-auto p-6">
        <div className="mb-5 flex flex-wrap items-end gap-3">
          <div className="w-44">
            <label className="mb-1.5 block text-small text-text-secondary">
              Campaña
            </label>
            <Select value={campaign} onChange={(e) => setCampaign(e.target.value)}>
              <option value="">Todas</option>
              {campaigns?.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </Select>
          </div>
          <div className="w-44">
            <label className="mb-1.5 block text-small text-text-secondary">
              Ejecutivo
            </label>
            <Select value={agentId} onChange={(e) => setAgentId(e.target.value)}>
              <option value="">Todos</option>
              {agents?.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </Select>
          </div>
          <div className="w-40">
            <label className="mb-1.5 block text-small text-text-secondary">
              Desde
            </label>
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </div>
          <div className="w-40">
            <label className="mb-1.5 block text-small text-text-secondary">
              Hasta
            </label>
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>
          <div className="w-40">
            <label className="mb-1.5 block text-small text-text-secondary">
              Periodo rápido
            </label>
            <Select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              aria-label="Periodo"
              disabled={Boolean(dateFrom || dateTo)}
            >
              <option value="7d">Últimos 7 días</option>
              <option value="30d">Últimos 30 días</option>
              <option value="90d">Últimos 90 días</option>
            </Select>
          </div>
          {hasFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              <X size={16} />
              Limpiar
            </Button>
          )}
        </div>

        {isLoading && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        )}

        {error && <ErrorState message={getErrorMessage(error)} />}

        {data && data.total_calls === 0 && (
          <EmptyState
            icon={<Phone size={48} />}
            title={hasFilters ? 'Sin resultados' : 'Aún no hay llamadas analizadas'}
            description={
              hasFilters
                ? 'No hay llamadas que coincidan con los filtros seleccionados.'
                : 'Sube tu primera llamada para empezar a ver métricas del equipo.'
            }
            action={
              hasFilters ? undefined : (
                <Link
                  href="/calls/new"
                  className="rounded-lg bg-accent-primary px-4 py-2 text-body text-white"
                >
                  Subir llamada
                </Link>
              )
            }
          />
        )}

        {data && data.total_calls > 0 && (
          <div className="flex flex-col gap-6">
            {/* KPIs */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <KpiCard
                label="Llamadas analizadas"
                value={data.total_calls.toLocaleString('es-PE')}
                icon={<Phone size={18} />}
              />
              <KpiCard
                label="Score promedio del equipo"
                value={data.average_score.toFixed(1)}
                icon={<Star size={18} />}
              />
              <KpiCard
                label="Tendencia"
                value={data.score_trend}
                delta={data.score_trend}
                icon={<TrendingUp size={18} />}
              />
            </div>

            {/* Gráficos */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <Card>
                <CardTitle className="mb-4">
                  Distribución de scores
                </CardTitle>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={data.score_distribution}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="var(--border)"
                    />
                    <XAxis
                      dataKey="range"
                      tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                    />
                    <YAxis
                      tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                    />
                    <Tooltip
                      contentStyle={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border)',
                        borderRadius: 8,
                        color: 'var(--text-primary)',
                      }}
                    />
                    <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                      {data.score_distribution.map((d) => (
                        <Cell
                          key={d.range}
                          fill={DISTRIBUTION_COLORS[d.range] ?? 'var(--info)'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              <Card>
                <CardTitle className="mb-4">Llamadas por día</CardTitle>
                <ResponsiveContainer width="100%" height={240}>
                  <LineChart data={data.calls_by_day}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="var(--border)"
                    />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
                    />
                    <YAxis
                      tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                    />
                    <Tooltip
                      contentStyle={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border)',
                        borderRadius: 8,
                        color: 'var(--text-primary)',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="var(--accent-primary)"
                      strokeWidth={2}
                      dot={{ fill: 'var(--accent-primary)' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Rankings */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <Card>
                <CardTitle className="mb-3">Top 5 mejor performance</CardTitle>
                <RankingList items={data.top_performers} />
              </Card>
              <Card>
                <CardTitle className="mb-3">
                  Top 5 oportunidad de mejora
                </CardTitle>
                <RankingList items={data.improvement_opportunities} />
              </Card>
            </div>
          </div>
        )}
      </main>
    </>
  );
}

function RankingList({ items }: { items: AgentScore[] }) {
  if (items.length === 0) {
    return <p className="text-small text-text-muted">Sin datos suficientes.</p>;
  }
  const cls =
    'flex items-center justify-between rounded-lg px-2 py-2 transition-colors';
  return (
    <ul className="flex flex-col gap-2">
      {items.map((item, i) => {
        const content = (
          <>
            <span className="flex items-center gap-3">
              <span className="text-small font-bold text-text-muted">
                {i + 1}
              </span>
              <span className="text-body text-text-primary">{item.name}</span>
              {!item.registered && (
                <span
                  className="rounded-md bg-warning/15 px-1.5 py-0.5
                             text-small font-medium text-warning"
                >
                  Sin registrar
                </span>
              )}
            </span>
            <ScoreBadge score={Math.round(item.avg_score)} />
          </>
        );
        return (
          <li key={`${item.agent_id ?? 'd'}-${item.name}-${i}`}>
            {item.registered && item.agent_id ? (
              <Link
                href={`/agents/${item.agent_id}`}
                className={`${cls} hover:bg-bg-accent/40`}
              >
                {content}
              </Link>
            ) : (
              <div className={cls}>{content}</div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
