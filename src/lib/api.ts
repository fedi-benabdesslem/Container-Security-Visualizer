import axios from 'axios';

// Configure base URL for API calls
const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface HistoricalEvent {
  id: string;
  timestamp: number;
  type: string;
  containerId: string;
  containerName: string;
  data: any;
}

export interface Container {
  id: string;
  name: string;
  image: string;
  status: string;
  riskLevel: 'safe' | 'warning' | 'critical';
}

export const api = {
  // Fetch historical events
  getHistory: async (params?: {
    startTime?: number;
    endTime?: number;
    containerId?: string;
    eventType?: string;
  }): Promise<HistoricalEvent[]> => {
    const response = await apiClient.get('/history', { params });
    return response.data;
  },

  // Fetch all containers
  getContainers: async (): Promise<Container[]> => {
    const response = await apiClient.get('/containers');
    return response.data;
  },

  // Fetch container details
  getContainerDetails: async (containerId: string): Promise<Container> => {
    const response = await apiClient.get(`/containers/${containerId}`);
    return response.data;
  },

  // Fetch container metrics
  getContainerMetrics: async (containerId: string): Promise<any> => {
    const response = await apiClient.get(`/containers/${containerId}/metrics`);
    return response.data;
  },
};
