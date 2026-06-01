/** Tipos TypeScript que reflejan los contratos de la API del backend. */

export type CallStatus =
  | 'QUEUED'
  | 'TRANSCRIBING'
  | 'ANALYZING'
  | 'DONE'
  | 'ERROR';

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  last_login?: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Agent {
  id: number;
  name: string;
  email?: string | null;
  campaign?: string | null;
  start_date?: string | null;
  photo_url?: string | null;
  active: boolean;
}

export interface AgentDetail extends Agent {
  total_calls: number;
  average_score?: number | null;
}

export interface AgentRef {
  id: number;
  name: string;
  campaign?: string | null;
}

export interface Recommendation {
  priority: 'high' | 'medium' | 'low';
  dimension: string;
  title: string;
  description: string;
}

export interface TranscriptionSegment {
  start: number;
  end: number;
  speaker: string;
  text: string;
}

export interface Transcription {
  full_text: string;
  segments: TranscriptionSegment[];
  language?: string | null;
}

export interface Analysis {
  global_score: number;
  dimension_scores: Record<string, number>;
  recommendations: Recommendation[];
  summary?: string | null;
  ai_provider?: string | null;
  ai_model?: string | null;
  team_average?: Record<string, number> | null;
}

export interface CallListItem {
  id: number;
  /** null si la llamada aún no está asignada a un ejecutivo registrado. */
  agent?: AgentRef | null;
  detected_agent_name?: string | null;
  call_date?: string | null;
  duration_seconds?: number | null;
  status: CallStatus;
  global_score?: number | null;
  created_at: string;
}

export interface CallList {
  items: CallListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CallDetail {
  id: number;
  agent?: AgentRef | null;
  detected_agent_name?: string | null;
  responsible?: string | null;
  audio_url: string;
  audio_filename?: string | null;
  duration_seconds?: number | null;
  status: CallStatus;
  language: string;
  call_date?: string | null;
  campaign_type?: string | null;
  call_reason?: string | null;
  error_message?: string | null;
  created_at: string;
  processed_at?: string | null;
  transcription?: Transcription | null;
  analysis?: Analysis | null;
}

export interface CallStatusInfo {
  id: number;
  status: CallStatus;
  progress_percent: number;
  error_message?: string | null;
}

export interface AgentScore {
  /** null cuando el ejecutivo fue detectado por la IA pero no está registrado. */
  agent_id?: number | null;
  name: string;
  avg_score: number;
  total_calls: number;
  registered: boolean;
}

export interface DashboardSummary {
  total_calls: number;
  average_score: number;
  score_trend: string;
  calls_by_day: { date: string; count: number; avg_score?: number | null }[];
  score_distribution: { range: string; count: number }[];
  top_performers: AgentScore[];
  improvement_opportunities: AgentScore[];
}

export interface AgentDashboard {
  agent: { id: number; name: string; campaign?: string | null };
  total_calls: number;
  average_score: number;
  score_trend: string;
  dimension_averages: Record<string, number>;
  team_dimension_averages: Record<string, number>;
  strengths: string[];
  improvement_areas: string[];
  timeline: { date: string; avg_score: number }[];
}

export interface RubricCriterion {
  name: string;
  enabled: boolean;
}

export interface RubricDimension {
  dimension_key: string;
  dimension_name: string;
  description?: string | null;
  weight: number;
  display_order?: number | null;
  criteria: RubricCriterion[];
}

/** Forma enviada al guardar la rúbrica (dimension_key vacío = categoría nueva). */
export interface RubricDimensionInput {
  dimension_key?: string;
  dimension_name: string;
  description?: string | null;
  weight: number;
  criteria: RubricCriterion[];
}

export interface AppSettings {
  default_language: string;
  ai_provider: string;
  whisper_provider: string;
}
