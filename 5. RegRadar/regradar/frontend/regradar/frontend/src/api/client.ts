import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export const regulationApi = {
  createSession: async (domains: string[]) => {
    const { data } = await client.post('/session', { domains });
    return data;
  },

  fetchDomains: async () => {
    const { data } = await client.get('/domains');
    return data;
  },

  fetchRegulations: async (
    sessionId: string,
    skip: number = 0,
    limit: number = 20,
    filters?: Record<string, any>,
  ) => {
    const params: Record<string, any> = { skip, limit };
    if (filters?.source) params.source = filters.source;
    if (filters?.impact) params.impact_level = filters.impact;
    const { data } = await client.get('/regulations', {
      params,
      headers: { 'X-Session-ID': sessionId },
    });
    return data;
  },

  fetchRegulationDetail: async (regulationId: string, sessionId: string) => {
    const { data } = await client.get(`/regulations/${regulationId}`, {
      headers: { 'X-Session-ID': sessionId },
    });
    return data;
  },

  fetchStats: async (sessionId: string) => {
    const { data } = await client.get('/stats', {
      headers: { 'X-Session-ID': sessionId },
    });
    return data;
  },
};
