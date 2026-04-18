import axios from 'axios';
import { useAuthStore } from './store';

const getApiClient = () => {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const client = axios.create({
    baseURL: API_BASE,
    headers: { 'Content-Type': 'application/json' },
  });

  client.interceptors.request.use((config) => {
    const state = useAuthStore.getState();
    const token =
      state.token ||
      (typeof window !== 'undefined'
        ? localStorage.getItem('auth_token')
        : null);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        const isLoginPage = window.location.pathname === '/login';
        const isHydrated = useAuthStore.getState()._hasHydrated;
        if (isHydrated && !isLoginPage) {
          useAuthStore.getState().clearAuth();
          window.location.href = '/login';
        }
      }
      return Promise.reject(error);
    }
  );

  return client;
};

let _apiClient: ReturnType<typeof axios.create> | null = null;
export const apiClient = new Proxy({} as ReturnType<typeof axios.create>, {
  get(_, prop) {
    if (!_apiClient) _apiClient = getApiClient();
    return (_apiClient as any)[prop];
  },
});

// ── Job API ──────────────────────────────────────────────────────────
export const jobsAPI = {
  list: (params: {
    page?: number;
    limit?: number;
    search?: string;
    category?: string;
    location?: string;
    job_type?: string;
    source?: string;
  }) => apiClient.get('/api/jobs', { params }),

  get: (id: string) => apiClient.get(`/api/jobs/${id}`),

  getCategories: () => apiClient.get('/api/jobs/filters/categories'),
  getSources: () => apiClient.get('/api/jobs/filters/sources'),
  getLocations: () => apiClient.get('/api/jobs/filters/locations'),
};

// ── Applications API ─────────────────────────────────────────────────
export const applicationsAPI = {
  list: (params: { status?: string; page?: number; limit?: number }) =>
    apiClient.get('/api/applications', { params }),

  get: (jobId: string) => apiClient.get(`/api/applications/${jobId}`),

  save: (jobId: string) => apiClient.post(`/api/applications/${jobId}/save`),

  unsave: (jobId: string) =>
    apiClient.delete(`/api/applications/${jobId}/save`),

  update: (jobId: string, data: { status?: string; notes?: string }) =>
    apiClient.patch(`/api/applications/${jobId}`, data),
};

// ── Pipeline API ─────────────────────────────────────────────────────
export const pipelineAPI = {
  run: (params?: { job_filter?: string }) =>
    apiClient.post('/api/pipeline/run', {}, { params }),

  getHistory: (limit?: number) =>
    apiClient.get('/api/pipeline/history', { params: { limit } }),

  getStatus: () => apiClient.get('/api/pipeline/status'),
};

// ── Stats API ────────────────────────────────────────────────────────
export const statsAPI = {
  getOverview: () => apiClient.get('/api/stats'),
  getAnalytics: () => apiClient.get('/api/stats'),
  getByCategory: () => apiClient.get('/api/stats/by-category'),
  getBySource: () => apiClient.get('/api/stats/by-source'),
};

export default apiClient;