'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Users, X } from 'lucide-react';
import { useAgents, useCreateAgent } from '@/lib/queries';
import { getErrorMessage } from '@/lib/api';
import { Header } from '@/components/layout/header';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { EmptyState, ErrorState, Skeleton } from '@/components/ui/feedback';

/** Listado y alta de ejecutivos. */
export default function AgentsPage() {
  const router = useRouter();
  const { data: agents, isLoading, error } = useAgents();
  const createAgent = useCreateAgent();

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [campaign, setCampaign] = useState('');
  const [startDate, setStartDate] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!name.trim()) {
      setFormError('El nombre es obligatorio.');
      return;
    }
    try {
      const created = await createAgent.mutateAsync({
        name: name.trim(),
        email: email.trim() || undefined,
        campaign: campaign.trim() || undefined,
        start_date: startDate || undefined,
      });
      setName('');
      setEmail('');
      setCampaign('');
      setStartDate('');
      setShowForm(false);
      const linked = (created as { linked_calls?: number }).linked_calls ?? 0;
      setSuccessMsg(
        linked > 0
          ? `Ejecutivo creado. Se le vincularon ${linked} llamada(s) que la IA había detectado con su nombre.`
          : 'Ejecutivo creado correctamente.',
      );
    } catch (err) {
      setFormError(getErrorMessage(err));
    }
  }

  return (
    <>
      <Header title="Ejecutivos" />
      <main className="flex-1 overflow-y-auto p-6">
        <div className="mb-5 flex items-center justify-between">
          <p className="text-body text-text-secondary">
            Equipo de ejecutivos evaluados
          </p>
          <Button
            onClick={() => {
              setShowForm((v) => !v);
              setSuccessMsg(null);
            }}
          >
            {showForm ? <X size={18} /> : <Plus size={18} />}
            {showForm ? 'Cancelar' : 'Nuevo ejecutivo'}
          </Button>
        </div>

        {successMsg && (
          <div className="mb-5 rounded-card border border-success/30 bg-success/10
                          px-4 py-3 text-body text-success">
            {successMsg}
          </div>
        )}

        {/* Formulario de alta */}
        {showForm && (
          <Card className="mb-5">
            <CardTitle className="mb-4">Nuevo ejecutivo</CardTitle>
            <form
              onSubmit={onCreate}
              className="grid grid-cols-1 gap-4 sm:grid-cols-2"
            >
              <div>
                <Label htmlFor="name">Nombre completo *</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="campaign">Campaña asignada</Label>
                <Input
                  id="campaign"
                  value={campaign}
                  onChange={(e) => setCampaign(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="startDate">Fecha de ingreso</Label>
                <Input
                  id="startDate"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              {formError && (
                <div className="sm:col-span-2">
                  <ErrorState message={formError} />
                </div>
              )}
              <div className="sm:col-span-2">
                <Button type="submit" disabled={createAgent.isPending}>
                  Guardar ejecutivo
                </Button>
              </div>
            </form>
          </Card>
        )}

        {isLoading && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
        )}

        {error && <ErrorState message={getErrorMessage(error)} />}

        {agents && agents.length === 0 && (
          <EmptyState
            icon={<Users size={48} />}
            title="Sin ejecutivos"
            description="Crea el primer ejecutivo para empezar a subir llamadas."
          />
        )}

        {agents && agents.length > 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {agents.map((agent) => (
              <Card
                key={agent.id}
                onClick={() => router.push(`/agents/${agent.id}`)}
                className="lift-on-hover cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="flex h-11 w-11 items-center justify-center rounded-full
                               bg-accent-secondary text-body font-bold text-white"
                  >
                    {agent.name
                      .split(' ')
                      .map((p) => p[0])
                      .slice(0, 2)
                      .join('')
                      .toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-body font-semibold text-text-primary">
                      {agent.name}
                    </p>
                    <p className="truncate text-small text-text-muted">
                      {agent.campaign ?? 'Sin campaña'}
                    </p>
                  </div>
                  {!agent.active && (
                    <span className="ml-auto rounded-control bg-danger/15 px-2 py-0.5 text-small text-danger">
                      Inactivo
                    </span>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
