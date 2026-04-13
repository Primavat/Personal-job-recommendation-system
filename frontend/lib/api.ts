import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
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
  getOverview: () => apiClient.get('/api/stats/overview'),
  getAnalytics: () => apiClient.get('/api/stats'),
  getByCategory: () => apiClient.get('/api/stats/by-category'),
  getBySource: () => apiClient.get('/api/stats/by-source'),
};

export default apiClient;
