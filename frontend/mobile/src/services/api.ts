/**
 * Mobile API Service Client.
 * Communicates with the backend REST API endpoints.
 */

const API_BASE_URL = 'http://localhost:5000/api'; // Or Android emulator 10.0.2.2:5000

export const detectNetworkFromPrefix = (phone: string): 'MTN' | 'TELECEL' | 'AT' | null => {
  const clean = phone.replace(/[^\d]/g, '');
  let localDigits = clean;
  if (clean.startsWith('233')) {
    localDigits = '0' + clean.slice(3);
  }
  const prefix = localDigits.slice(0, 3);

  if (['024', '025', '053', '054', '055', '059'].includes(prefix)) return 'MTN';
  if (['020', '050'].includes(prefix)) return 'TELECEL';
  if (['026', '027', '056', '057'].includes(prefix)) return 'AT';
  return null;
};

export const mobileApi = {
  getProducts: async () => {
    const res = await fetch(`${API_BASE_URL}/products`);
    return res.json();
  },

  getDataBundles: async (networkCode?: string) => {
    const url = networkCode
      ? `${API_BASE_URL}/data-bundles?network=${networkCode}`
      : `${API_BASE_URL}/data-bundles`;
    const res = await fetch(url);
    return res.json();
  },

  createOrder: async (token: string, payload: {
    order_type: string;
    recipient_phone: string;
    network_code: string;
    amount?: number;
    data_bundle_plan_id?: number;
  }) => {
    const res = await fetch(`${API_BASE_URL}/orders`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    return res.json();
  },

  requestMoMoPayment: async (token: string, orderId: number, momoPhone: string) => {
    const res = await fetch(`${API_BASE_URL}/payments/momo/request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        order_id: orderId,
        momo_phone: momoPhone,
      }),
    });
    return res.json();
  },

  pollPaymentStatus: async (token: string, transactionReference: string) => {
    const res = await fetch(`${API_BASE_URL}/payments/momo/status/${transactionReference}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return res.json();
  },

  getOrdersHistory: async (token: string) => {
    const res = await fetch(`${API_BASE_URL}/orders`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return res.json();
  },
};
