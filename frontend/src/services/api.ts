import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'https://gigshield-cgp7rarsh-rohitkumarrohit7970-creators-projects.vercel.app/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: (phone: string, password: string) =>
    api.post('/auth/login', { phone, password }),
  register: (data: {
    phone: string;
    name: string;
    delivery_platform: string;
    platform_id: string;
    city_id: number;
    primary_zone_id: number;
    password: string;
    upi_id?: string;
  }) => api.post('/auth/register', data),
  calculatePremium: (data: {
    city_id: number;
    zone_id: number;
    avg_daily_income: number;
    coverage_hours: number;
  }) => api.post('/auth/premium', data),
};

export const workerApi = {
  getMe: () => api.get('/workers/me'),
  getMyEarnings: () => api.get('/workers/me/earnings'),
  getMyPolicy: () => api.get('/workers/me/policy'),
  getMyClaims: () => api.get('/workers/me/claims'),
  getCities: () => api.get('/workers/cities'),
  getCityZones: (cityId: number) => api.get(`/workers/cities/${cityId}/zones`),
  getActiveDisruptions: () => api.get('/workers/disruptions/active'),
  updateProfile: (data: { name?: string; upi_id?: string }) => 
    api.patch('/workers/me', data),
};

export const policyApi = {
  create: (data: {
    worker_id: number;
    zone_id: number;
    coverage_hours: number;
    weekly_premium: number;
  }) => api.post('/policies/create', data),
};

export const claimsApi = {
  getAll: (status?: string) => api.get('/claims', { params: { status } }),
  getById: (id: number) => api.get(`/claims/${id}`),
  create: (data: { disruption_event_id: number }) => api.post('/claims', data),
  approve: (id: number, reviewNotes?: string) =>
    api.post(`/claims/${id}/approve`, null, { params: { review_notes: reviewNotes } }),
  reject: (id: number, reviewNotes: string) =>
    api.post(`/claims/${id}/reject`, null, { params: { review_notes: reviewNotes } }),
  autoProcess: (id: number) => api.post(`/claims/${id}/auto-process`),
};

export const adminApi = {
  getStats: () => api.get('/admin/stats'),
  getActiveDisruptions: () => api.get('/admin/disruptions/active'),
  simulateDisruption: (zoneId: number, triggerType: string) =>
    api.post('/admin/disruptions/simulate', null, { params: { zone_id: zoneId, trigger_type: triggerType } }),
  getPendingClaims: () => api.get('/admin/claims/pending'),
  getReviewQueue: () => api.get('/admin/claims/review-queue'),
};

export const paymentsApi = {
  createOrder: (amount: number, policyId: number) =>
    api.post('/payments/create-order', { amount, policy_id: policyId }),
  verifyPayment: (razorpay_order_id: string, razorpay_payment_id: string, razorpay_signature: string) =>
    api.post('/payments/verify', { razorpay_order_id, razorpay_payment_id, razorpay_signature }),
  payout: (worker_upi: string, amount: number, claimId: number) =>
    api.post('/payments/payout', { worker_upi, amount, claim_id: claimId }),
};

export default api;
