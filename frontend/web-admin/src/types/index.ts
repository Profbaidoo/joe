export interface User {
  id: number;
  username: string;
  email: string;
  phone_number: string;
  role: 'ADMIN' | 'AGENT' | 'CUSTOMER';
  is_active: boolean;
  agent_profile?: AgentProfile;
  customer_profile?: CustomerProfile;
}

export interface AgentProfile {
  id: number;
  agent_code: string;
  business_name: string;
  location: string;
  commission_balance: number;
  wallet_balance: number;
  status: string;
}

export interface CustomerProfile {
  id: number;
  full_name: string;
  momo_number?: string;
  momo_network?: string;
  wallet_balance: number;
}

export interface Network {
  id: number;
  code: 'MTN' | 'TELECEL' | 'AT';
  name: string;
  is_active: boolean;
  airtime_supported: boolean;
  data_supported: boolean;
}

export interface Product {
  id: number;
  code: string;
  name: string;
  category: string;
  network_code?: string;
  wholesale_price: number;
  retail_price: number;
  min_amount: number;
  max_amount: number;
  is_active: boolean;
}

export interface DataBundlePlan {
  id: number;
  plan_code: string;
  name: string;
  network_code: string;
  volume_mb: number;
  validity_days: number;
  wholesale_price: number;
  retail_price: number;
  is_active: boolean;
}

export interface Order {
  id: number;
  order_reference: string;
  user_id: number;
  agent_id?: number;
  order_type: string;
  recipient_phone: string;
  network_code: string;
  total_amount: number;
  fee_amount: number;
  net_amount: number;
  status: 'PENDING' | 'PAID' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'REFUNDED';
  payment_status: string;
  fulfillment_status: string;
  fulfillment_provider?: string;
  fulfillment_reference?: string;
  failure_reason?: string;
  created_at: string;
}

export interface Transaction {
  id: number;
  transaction_reference: string;
  order_id?: number;
  user_id: number;
  transaction_type: string;
  payment_method: string;
  amount: number;
  fee: number;
  net_amount: number;
  currency: string;
  status: 'PENDING' | 'PROCESSING' | 'SUCCESSFUL' | 'FAILED' | 'TIMED_OUT' | 'REVERSED';
  provider_name: string;
  provider_reference?: string;
  customer_phone: string;
  error_message?: string;
  created_at: string;
}

export interface DashboardMetrics {
  today_metrics: {
    sales_volume: number;
    order_count: number;
    airtime_sales: number;
    data_sales: number;
    bill_sales: number;
    successful_transactions: number;
    pending_transactions: number;
    failed_transactions: number;
  };
  financial_ledger_summary: {
    provider_clearing_balance: number;
    business_revenue_accumulated: number;
    fee_income: number;
    commission_expense: number;
    estimated_net_profit: number;
  };
  business_status: {
    active_agents: number;
    currency: string;
    timezone: string;
    provider_alert?: string;
  };
}
