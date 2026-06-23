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
  AgentPercentile,
  AgentRecommendations,
  AppSettings,
  CallDetail,
  CallList,
  CallStatusInfo,
  Campaign,
  CampaignAssistResult,
  CampaignDraft,
  CampaignExtractResult,
  CampaignKpi,
  DashboardAlert,
  DashboardSummary,
  RecommendationStat,
  RubricDimension,
  RubricDimensionInput,
  User,
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

/** Crea la cuenta de acceso (rol asesor) vinculada a un ejecutivo. */
export function useCreateAgentLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      email,
      password,
      name,
    }: {
      id: number;
      email: string;
      password: string;
      name?: string;
    }) => {
      const { data } = await api.post<User>(`/agents/${id}/login`, {
        email,
        password,
        name,
      });
      return data;
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['agent', vars.id] });
    },
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

export interface DashboardFilters {
  period?: string;
  campaign?: string;
  agent_id?: number;
  date_from?: string;
  date_to?: string;
}

export function useDashboardSummary(filters: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', filters],
    queryFn: async () => {
      const { data } = await api.get<DashboardSummary>('/dashboard/summary', {
        params: filters,
      });
      return data;
    },
  });
}

export function useCampaigns() {
  return useQuery({
    queryKey: ['campaigns'],
    queryFn: async () => {
      const { data } = await api.get<string[]>('/dashboard/campaigns');
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

export function useDashboardByCampaign(filters: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard-by-campaign', filters],
    queryFn: async () => {
      const { data } = await api.get<CampaignKpi[]>('/dashboard/by-campaign', {
        params: filters,
      });
      return data;
    },
  });
}

export function useDashboardAlerts(filters: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard-alerts', filters],
    queryFn: async () => {
      const { data } = await api.get<DashboardAlert[]>('/dashboard/alerts', {
        params: filters,
      });
      return data;
    },
  });
}

export function useTopRecommendations(filters: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard-top-recommendations', filters],
    queryFn: async () => {
      const { data } = await api.get<RecommendationStat[]>(
        '/dashboard/top-recommendations',
        { params: filters },
      );
      return data;
    },
  });
}

export function useAgentPercentile(id: number, period: string) {
  return useQuery({
    queryKey: ['agent-percentile', id, period],
    queryFn: async () => {
      const { data } = await api.get<AgentPercentile>(
        `/dashboard/agents/${id}/percentile`,
        { params: { period } },
      );
      return data;
    },
    enabled: Number.isFinite(id),
  });
}

export function useAgentRecommendations(id: number, period: string) {
  return useQuery({
    queryKey: ['agent-recommendations', id, period],
    queryFn: async () => {
      const { data } = await api.get<AgentRecommendations>(
        `/dashboard/agents/${id}/recommendations`,
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
    mutationFn: async (dimensions: RubricDimensionInput[]) => {
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

/* ------------------------------ Campañas ------------------------------ */

export function useCampaignList(params?: { active?: boolean; search?: string }) {
  return useQuery({
    queryKey: ['campaign-list', params],
    queryFn: async () => {
      const { data } = await api.get<Campaign[]>('/campaigns', { params });
      return data;
    },
  });
}

export function useCampaign(id: number) {
  return useQuery({
    queryKey: ['campaign', id],
    queryFn: async () => {
      const { data } = await api.get<Campaign>(`/campaigns/${id}`);
      return data;
    },
    enabled: Number.isFinite(id),
  });
}

export function useCreateCampaign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Campaign>) => {
      const { data } = await api.post<Campaign>('/campaigns', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaign-list'] }),
  });
}

export function useUpdateCampaign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<Campaign> & { id: number }) => {
      const { data } = await api.put<Campaign>(`/campaigns/${id}`, payload);
      return data;
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['campaign-list'] });
      qc.invalidateQueries({ queryKey: ['campaign', vars.id] });
    },
  });
}

export function useDeactivateCampaign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/campaigns/${id}`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaign-list'] }),
  });
}

/** Sube un PDF de nota de producto y devuelve la nota estructurada. */
export function useExtractCampaignPdf() {
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append('file', file);
      const { data } = await api.post<CampaignExtractResult>(
        '/campaigns/extract',
        form,
      );
      return data;
    },
  });
}

/** Pide a la IA que complete la nota de producto a partir de una descripción. */
export function useAssistCampaign() {
  return useMutation({
    mutationFn: async (payload: {
      description: string;
      current?: CampaignDraft;
    }) => {
      const { data } = await api.post<CampaignAssistResult>(
        '/campaigns/assist',
        payload,
      );
      return data;
    },
  });
}
