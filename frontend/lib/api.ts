import axios from 'axios';
import { useAuthStore } from './store';

const API_BASE = (typeof window !== 'undefined'
  ? process.env.NEXT_PUBLIC_API_URL
  : undefined) || 'http://localhost:8000';

const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true' || !process.env.NEXT_PUBLIC_API_URL;

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  if (typeof window === 'undefined') return config;
  const state = useAuthStore.getState();
  if (!state._hasHydrated) return config;
  const token = state.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (typeof window === 'undefined') return Promise.reject(error);
    if (DEMO_MODE && (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || !error.response)) {
      console.warn('Backend not available, using demo mode');
      return Promise.reject({ ...error, isDemoModeError: true });
    }
    if (error.response?.status === 401) {
      const isLoginPage = window.location.pathname === '/login';
      const isHydrated = useAuthStore.getState()._hasHydrated;
      if (isHydrated && !isLoginPage) {
        useAuthStore.getState().clearAuth();
        window.location.replace('/login');
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth API ─────────────────────────────────────────────────────────
export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post('/api/auth/login', { email, password }),
  register: (email: string, password: string, name: string) =>
    apiClient.post('/api/auth/register', { email, password, name }),
  updateProfile: (data: { name?: string; email?: string }) =>
    apiClient.patch('/api/auth/profile', data),
};

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
  unsave: (jobId: string) => apiClient.delete(`/api/applications/${jobId}/save`),
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