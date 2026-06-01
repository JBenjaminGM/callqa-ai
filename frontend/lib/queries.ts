'use client';

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import { api } from '@/lib/api';
import type {
  Agent,
  AgentDashboard,
  AgentDetail,
  AppSettings,
  CallDetail,
  CallList,
  CallStatusInfo,
  DashboardSummary,
  RubricDimension,
} from '@/types';

/* ----------------------------- Ejecutivos ----------------------------- */

export function useAgents(params?: { active?: boolean; search?: string }) {
  return useQuery({
    queryKey: ['agents', params],
    queryFn: async () => {
      const { data } = await api.get<Agent[]>('/agents', { params });
      return data;
    },
  });
}

export function useAgent(id: number) {
  return useQuery({
    queryKey: ['agent', id],
    queryFn: async () => {
      const { data } = await api.get<AgentDetail>(`/agents/${id}`);
      return data;
    },
    enabled: Number.isFinite(id),
  });
}

export function useCreateAgent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Agent>) => {
      const { data } = await api.post<Agent>('/agents', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  });
}

export function useUpdateAgent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<Agent> & { id: number }) => {
      const { data } = await api.put<Agent>(`/agents/${id}`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['agents'] });
      qc.invalidateQueries({ queryKey: ['agent'] });
    },
  });
}

export function useDeactivateAgent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/agents/${id}`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  });
}

/* ------------------------------ Llamadas ------------------------------ */

export interface CallFilters {
  agent_id?: number;
  status?: string;
  min_score?: number;
  max_score?: number;
  date_from?: string;
  date_to?: string;
  unassigned?: boolean;
  page?: number;
  page_size?: number;
}

export function useCalls(filters: CallFilters) {
  return useQuery({
    queryKey: ['calls', filters],
    queryFn: async () => {
      const { data } = await api.get<CallList>('/calls', { params: filters });
      return data;
    },
  });
}

export function useCall(id: number, pollWhileProcessing = false) {
  return useQuery({
    queryKey: ['call', id],
    queryFn: async () => {
      const { data } = await api.get<CallDetail>(`/calls/${id}`);
      return data;
    },
    enabled: Number.isFinite(id),
    // Mientras la llamada se procesa, refresca cada 5 segundos.
    refetchInterval: (query) => {
      if (!pollWhileProcessing) return false;
      const status = query.state.data?.status;
      return status === 'DONE' || status === 'ERROR' ? false : 5000;
    },
  });
}

export function useCallStatus(id: number, enabled: boolean) {
  return useQuery({
    queryKey: ['call-status', id],
    queryFn: async () => {
      const { data } = await api.get<CallStatusInfo>(`/calls/${id}/status`);
      return data;
    },
    enabled,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'DONE' || status === 'ERROR' ? false : 5000;
    },
  });
}

export function useRetryCall() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.post(`/calls/${id}/retry`);
    },
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ['call', id] });
      qc.invalidateQueries({ queryKey: ['calls'] });
    },
  });
}

export function useDeleteCall() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/calls/${id}`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['calls'] }),
  });
}

export function useAssignCall() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      agentId,
      applyToSameName,
    }: {
      id: number;
      agentId: number;
      applyToSameName?: boolean;
    }) => {
      const { data } = await api.put(`/calls/${id}/assign`, {
        agent_id: agentId,
        apply_to_same_name: applyToSameName ?? false,
      });
      return data;
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['call', vars.id] });
      qc.invalidateQueries({ queryKey: ['calls'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

/* ------------------------------ Dashboard ----------------------------- */

export function useDashboardSummary(period: string) {
  return useQuery({
    queryKey: ['dashboard', period],
    queryFn: async () => {
      const { data } = await api.get<DashboardSummary>('/dashboard/summary', {
        params: { period },
      });
      return data;
    },
  });
}

export function useAgentDashboard(id: number, period: string) {
  return useQuery({
    queryKey: ['agent-dashboard', id, period],
    queryFn: async () => {
      const { data } = await api.get<AgentDashboard>(
        `/dashboard/agents/${id}`,
        { params: { period } },
      );
      return data;
    },
    enabled: Number.isFinite(id),
  });
}

/* ----------------------------- Configuración --------------------------- */

export function useRubric() {
  return useQuery({
    queryKey: ['rubric'],
    queryFn: async () => {
      const { data } = await api.get<RubricDimension[]>('/config/rubric');
      return data;
    },
  });
}

export function useUpdateRubric() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (
      dimensions: { dimension_key: string; weight: number }[],
    ) => {
      const { data } = await api.put('/config/rubric', { dimensions });
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['rubric'] }),
  });
}

export function useSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const { data } = await api.get<AppSettings>('/config/settings');
      return data;
    },
  });
}

export function useUpdateSettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<AppSettings>) => {
      const { data } = await api.put('/config/settings', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings'] }),
  });
}
