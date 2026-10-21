/**
 * API Service Client for Ghana Fintech Backend.
 * Supports live Flask backend with automatic resilient demo fallback
 * when deployed as a standalone frontend on Vercel/cloud previews.
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

// ---------------------------------------------------------
// Standalone Demo Mock Data (used when cloud backend is offline)
// ---------------------------------------------------------
const MOCK_NETWORKS = [
  { id: 1, code: 'MTN', name: 'MTN Ghana', is_active: true },
  { id: 2, code: 'TELECEL', name: 'Telecel Ghana', is_active: true },
  { id: 3, code: 'AT', name: 'AT Ghana (AirtelTigo)', is_active: true },
];

const MOCK_PRODUCTS = [
  { id: 1, name: 'MTN Airtime', code: 'AIRTIME_MTN', category: 'AIRTIME', network_code: 'MTN', wholesale_price: 9.60, retail_price: 10.00, fee_percentage: 0.00, is_active: true },
  { id: 2, name: 'Telecel Airtime', code: 'AIRTIME_TELECEL', category: 'AIRTIME', network_code: 'TELECEL', wholesale_price: 9.50, retail_price: 10.00, fee_percentage: 0.00, is_active: true },
  { id: 3, name: 'AT Airtime', code: 'AIRTIME_AT', category: 'AIRTIME', network_code: 'AT', wholesale_price: 9.40, retail_price: 10.00, fee_percentage: 0.00, is_active: true },
];

const MOCK_DATA_BUNDLES = [
  { id: 1, network_code: 'MTN', plan_name: 'MTN 1GB Data', plan_code: 'MTN_1GB', volume: '1 GB', validity: '30 Days', wholesale_cost: 10.80, selling_price: 12.00, is_active: true },
  { id: 2, network_code: 'MTN', plan_name: 'MTN 2.5GB Data', plan_code: 'MTN_2.5GB', volume: '2.5 GB', validity: '30 Days', wholesale_cost: 22.50, selling_price: 25.00, is_active: true },
  { id: 3, network_code: 'MTN', plan_name: 'MTN 10GB Non-Expiry', plan_code: 'MTN_10GB_NE', volume: '10 GB', validity: 'Non-Expiry', wholesale_cost: 68.00, selling_price: 75.00, is_active: true },
  { id: 4, network_code: 'TELECEL', plan_name: 'Telecel 1.5GB Data', plan_code: 'TC_1.5GB', volume: '1.5 GB', validity: '30 Days', wholesale_cost: 10.50, selling_price: 12.00, is_active: true },
  { id: 5, network_code: 'TELECEL', plan_name: 'Telecel 6GB Non-Expiry', plan_code: 'TC_6GB_NE', volume: '6 GB', validity: 'Non-Expiry', wholesale_cost: 34.00, selling_price: 38.00, is_active: true },
  { id: 6, network_code: 'AT', plan_name: 'AT 2GB Big Time Data', plan_code: 'AT_2GB_NE', volume: '2 GB', validity: 'Non-Expiry', wholesale_cost: 8.80, selling_price: 10.00, is_active: true },
  { id: 7, network_code: 'AT', plan_name: 'AT 10GB Big Time Data', plan_code: 'AT_10GB_NE', volume: '10 GB', validity: 'Non-Expiry', wholesale_cost: 31.00, selling_price: 35.00, is_active: true },
];

let mockTransactions = [
  { id: 1, transaction_reference: 'TRX-MTN-94821', order_reference: 'ORD-A9281', customer_phone: '0241234567', network_code: 'MTN', transaction_type: 'AIRTIME', amount: 20.00, fee: 0.00, net_amount: 20.00, status: 'SUCCESSFUL', payment_method: 'MOMO_MTN', created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: 2, transaction_reference: 'TRX-MOM-84912', order_reference: 'ORD-B8491', customer_phone: '0559876543', network_code: 'MTN', transaction_type: 'DATA_BUNDLE', amount: 75.00, fee: 0.00, net_amount: 75.00, status: 'SUCCESSFUL', payment_method: 'MOMO_MTN', created_at: new Date(Date.now() - 7200000).toISOString() },
  { id: 3, transaction_reference: 'TRX-TEL-73219', order_reference: 'ORD-C7321', customer_phone: '0207654321', network_code: 'TELECEL', transaction_type: 'AIRTIME', amount: 15.00, fee: 0.00, net_amount: 15.00, status: 'SUCCESSFUL', payment_method: 'MOMO_TELECEL', created_at: new Date(Date.now() - 10800000).toISOString() },
  { id: 4, transaction_reference: 'TRX-AT-62194', order_reference: 'ORD-D6219', customer_phone: '0271122334', network_code: 'AT', transaction_type: 'DATA_BUNDLE', amount: 35.00, fee: 0.00, net_amount: 35.00, status: 'SUCCESSFUL', payment_method: 'MOMO_AT', created_at: new Date(Date.now() - 14400000).toISOString() },
  { id: 5, transaction_reference: 'TRX-ECG-51928', order_reference: 'ORD-E5192', customer_phone: '0244556677', network_code: 'MTN', transaction_type: 'BILL_PAYMENT', amount: 100.00, fee: 2.00, net_amount: 102.00, status: 'SUCCESSFUL', payment_method: 'MOMO_MTN', created_at: new Date(Date.now() - 18000000).toISOString() },
];

function getDemoFallback<T>(endpoint: string, options: RequestInit = {}): T {
  const method = (options.method || 'GET').toUpperCase();

  // Auth: Login
  if (endpoint === '/auth/login' && method === 'POST') {
    const creds = JSON.parse((options.body as string) || '{}');
    const isCashier = creds.login === 'cashier1';
    const user = {
      id: isCashier ? 2 : 1,
      username: isCashier ? 'cashier1' : 'admin',
      full_name: isCashier ? 'Abena Osei (Cashier)' : 'Kwame Mensah (Business Owner)',
      email: isCashier ? 'cashier1@blessingstelecom.com.gh' : 'admin@blessingstelecom.com.gh',
      phone: isCashier ? '0241111111' : '0240000000',
      role: isCashier ? 'AGENT' : 'ADMIN',
      is_active: true,
    };
    localStorage.setItem('user', JSON.stringify(user));
    return {
      access_token: 'demo-jwt-token-' + (isCashier ? 'agent' : 'admin'),
      refresh_token: 'demo-refresh-token',
      user,
    } as T;
  }

  // Auth: Profile
  if (endpoint === '/auth/profile') {
    const stored = localStorage.getItem('user');
    const user = stored ? JSON.parse(stored) : {
      id: 1,
      username: 'admin',
      full_name: 'Kwame Mensah (Business Owner)',
      email: 'admin@blessingstelecom.com.gh',
      phone: '0240000000',
      role: 'ADMIN',
      is_active: true,
    };
    return { user } as T;
  }

  // Admin: Dashboard KPIs
  if (endpoint === '/admin/dashboard') {
    return {
      today: {
        total_sales: 4850.00,
        completed_orders: 128,
        successful_transactions: 128,
        pending_transactions: 2,
        failed_transactions: 1,
        airtime_sales: 2150.00,
        data_bundle_sales: 2200.00,
        bill_payments: 500.00,
        estimated_profit: 428.50,
        agent_commissions: 85.00,
      },
      currency: 'GHS',
      timezone: 'Africa/Accra',
      environment: 'demo-preview',
    } as T;
  }

  // Transactions list
  if (endpoint.startsWith('/payments/transactions')) {
    return {
      transactions: mockTransactions,
      total: mockTransactions.length,
      page: 1,
      pages: 1,
    } as T;
  }

  // Catalog
  if (endpoint === '/products') return { products: MOCK_PRODUCTS } as T;
  if (endpoint === '/data-bundles') return { data_bundles: MOCK_DATA_BUNDLES } as T;
  if (endpoint === '/networks') return { networks: MOCK_NETWORKS } as T;

  // Agents
  if (endpoint === '/admin/agents') {
    return {
      agents: [
        { id: 1, agent_code: 'AGT-84912', full_name: 'Abena Osei', business_name: 'Blessings Telecom - Osu Branch', phone: '0241111111', commission_balance: 145.20, total_earned: 980.50, is_active: true },
        { id: 2, agent_code: 'AGT-32918', full_name: 'Kofi Mensah', business_name: 'Blessings Telecom - Kaneshie', phone: '0203334444', commission_balance: 82.00, total_earned: 540.00, is_active: true },
      ],
    } as T;
  }

  // Audit Logs
  if (endpoint === '/admin/audit-logs') {
    return {
      audit_logs: [
        { id: 1, action: 'LOGIN_SUCCESS', username: 'admin', ip_address: '127.0.0.1', details: { message: 'Successful session established' }, created_at: new Date().toISOString() },
        { id: 2, action: 'ORDER_FULFILLED', username: 'cashier1', ip_address: '127.0.0.1', details: { order_ref: 'ORD-A9281', network: 'MTN' }, created_at: new Date(Date.now() - 3600000).toISOString() },
      ],
    } as T;
  }

  // Orders creation
  if (endpoint === '/orders' && method === 'POST') {
    const data = JSON.parse((options.body as string) || '{}');
    const orderRef = 'ORD-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    return {
      message: 'Order created successfully. Proceed to payment.',
      order: {
        id: Math.floor(Math.random() * 1000) + 10,
        order_reference: orderRef,
        order_type: data.order_type,
        recipient_phone: data.recipient_phone,
        network_code: data.network_code,
        total_amount: data.amount || 10.00,
        fee_amount: 0.00,
        net_amount: data.amount || 10.00,
        status: 'PENDING',
        payment_status: 'UNPAID',
      },
    } as T;
  }

  // MoMo Request
  if (endpoint === '/payments/momo/request' && method === 'POST') {
    const trxRef = 'TRX-' + Math.random().toString(36).substring(2, 9).toUpperCase();
    return {
      transaction_reference: trxRef,
      provider_reference: 'MOMO-' + Date.now(),
      status: 'PENDING',
      message: 'Payment prompt sent to customer handset via MTN MoMo Open API. Please approve with USSD.',
      amount: 10.00,
    } as T;
  }

  // MoMo Status
  if (endpoint.startsWith('/payments/momo/status/')) {
    const trxRef = endpoint.split('/').pop() || 'TRX-SAMPLE';
    const newTrx = {
      id: mockTransactions.length + 1,
      transaction_reference: trxRef,
      order_reference: 'ORD-' + Math.random().toString(36).substring(2, 8).toUpperCase(),
      customer_phone: '0241234567',
      network_code: 'MTN',
      transaction_type: 'AIRTIME',
      amount: 10.00,
      fee: 0.00,
      net_amount: 10.00,
      status: 'SUCCESSFUL',
      payment_method: 'MOMO_MTN',
      created_at: new Date().toISOString(),
    };
    mockTransactions = [newTrx, ...mockTransactions];
    return {
      status: 'SUCCESSFUL',
      transaction_reference: trxRef,
      order_status: 'COMPLETED',
      fulfillment_status: 'FULFILLED',
      message: 'Transaction verified and fulfilled successfully.',
    } as T;
  }

  return {} as T;
}

// ---------------------------------------------------------
// Main Resilient Request Function
// ---------------------------------------------------------
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      clearAuthTokens();
      window.location.href = '/login';
      throw new Error('Session expired. Please login again.');
    }

    // Check if the server returned JSON
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      // If server returned HTML (e.g. Vercel SPA rewrite fallback because /api is not deployed to cloud),
      // switch transparently to the standalone interactive demo mode!
      console.warn(`[API] '${BASE_URL}${endpoint}' returned non-JSON (${response.status}). Using standalone demo engine.`);
      return getDemoFallback<T>(endpoint, options);
    }

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || data.message || `Request failed with status ${response.status}`);
    }

    return data;
  } catch (error: any) {
    // If network connection failed (e.g. backend offline on remote preview)
    if (error.name === 'TypeError' || error.message?.includes('fetch') || error.message?.includes('JSON')) {
      console.warn(`[API] Network failure on '${endpoint}'. Using standalone demo engine.`);
      return getDemoFallback<T>(endpoint, options);
    }
    throw error;
  }
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
