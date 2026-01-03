import axios from 'axios';
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http:
const ROOT_URL = import.meta.env.VITE_API_BASE_URL || 'http:
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
export interface BackendEvent {
  id: number;
  timestamp_iso: string;
  timestamp_ns: number;
  monitor_type: 'syscall' | 'network';
  pid: number;
  uid: number;
  comm: string;
  container_id: string;
  container_name: string;
  container_image: string;
  container_status: string;
  argv?: string;
  event_type?: string;
  source_ip?: string;
  dest_ip?: string;
  source_port?: number;
  dest_port?: number;
  risk_score: number;
  categories: string[];
  is_security_relevant: boolean;
}
export interface EventsResponse {
  events: BackendEvent[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}
export interface AlertItem {
  id: number;
  timestamp_iso: string;
  container_name: string;
  comm: string;
  risk_score: number;
  categories: string[];
  description: string;
}
export interface Container {
  container_id: string;
  container_name: string;
  container_image: string;
  event_count: number;
  first_seen: string;
  last_seen: string;
  risk_level: 'low' | 'medium' | 'high';
}
export interface SummaryStats {
  total_events: number;
  total_containers: number;
  syscall_events: number;
  network_events: number;
  high_risk_events: number;
  timespan_start: string;
  timespan_end: string;
}
export interface TimelineData {
  timestamp: string;
  count: number;
  syscall_count: number;
  network_count: number;
}
export interface TimelineResponse {
  interval: string;
  data: TimelineData[];
}
export interface HealthResponse {
  status: string;
  database: string;
  version: string;
}
export const api = {
  checkHealth: async (): Promise<HealthResponse> => {
    const response = await axios.get(`${ROOT_URL}/health`);
    return response.data;
  },
  getEvents: async (params?: {
    start_time?: number;
    end_time?: number;
    monitor_type?: 'syscall' | 'network';
    container_id?: string;
    container_name?: string;
    min_risk_score?: number;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<EventsResponse> => {
    const response = await apiClient.get('/events', { params });
    return response.data;
  },
  getAlerts: async (limit: number = 50): Promise<AlertItem[]> => {
    const response = await apiClient.get('/alerts', { params: { limit } });
    return response.data;
  },
  getSummaryStats: async (): Promise<SummaryStats> => {
    const response = await apiClient.get('/stats/summary');
    return response.data;
  },
  getTimeline: async (params?: {
    interval?: '1m' | '5m' | '15m' | '1h' | '6h' | '1d';
    start_time?: number;
    end_time?: number;
  }): Promise<TimelineResponse> => {
    const response = await apiClient.get('/stats/timeline', { params });
    return response.data;
  },
  getContainers: async (): Promise<Container[]> => {
    const response = await apiClient.get('/containers');
    return response.data;
  },
  getContainerEvents: async (containerId: string, limit: number = 100): Promise<{ events: BackendEvent[] }> => {
    const response = await apiClient.get(`/containers/${containerId}/events`, { params: { limit } });
    return response.data;
  },
};
