/**
 * API Service Client for Ghana Fintech Backend.
 */

const BASE_URL = (import.meta.env.VITE_API_URL as string) || '/api';

export function getAuthToken(): string | null {
  return localStorage.getItem('access_token');
}

export function setAuthTokens(access: string, refresh: string) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

export function clearAuthTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearAuthTokens();
    window.location.href = '/login';
    throw new Error('Session expired. Please login again.');
  }

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || data.message || `Request failed with status ${response.status}`);
  }

  return data;
}

export const api = {
  // Auth
  login: (credentials: { login: string; password: string }) =>
    request<{ access_token: string; refresh_token: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  getProfile: () => request<{ user: any }>('/auth/profile'),

  // Dashboard & Admin
  getDashboardKPIs: () => request<any>('/admin/dashboard'),

  getTransactions: (page = 1, status = '') =>
    request<{ transactions: any[]; total: number; page: number; pages: number }>(
      `/payments/transactions?page=${page}${status ? `&status=${status}` : ''}`
    ),

  getProducts: () => request<{ products: any[] }>('/products'),
  getDataBundles: () => request<{ data_bundles: any[] }>('/data-bundles'),
  getNetworks: () => request<{ networks: any[] }>('/networks'),

  updatePricing: (productId: number, data: { retail_price?: number; wholesale_price?: number; is_active?: boolean }) =>
    request<any>(`/admin/pricing/${productId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  getAgents: () => request<{ agents: any[] }>('/admin/agents'),
  createAgent: (agentData: any) =>
    request<any>('/admin/agents', {
      method: 'POST',
      body: JSON.stringify(agentData),
    }),

  getAuditLogs: () => request<{ audit_logs: any[] }>('/admin/audit-logs'),

  // MoMo & Payment Operations
  createOrder: (orderData: { order_type: string; recipient_phone: string; network_code: string; amount?: number; data_bundle_plan_id?: number }) =>
    request<{ message: string; order: any }>('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    }),

  requestMoMoPayment: (orderId: number, momoPhone: string) =>
    request<any>('/payments/momo/request', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId, momo_phone: momoPhone }),
    }),

  checkMoMoStatus: (reference: string) =>
    request<any>(`/payments/momo/status/${reference}`),
};
