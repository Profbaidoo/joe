import React, { useEffect, useState } from 'react';
import { 
  Banknote, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Smartphone, 
  Wifi, 
  Users, 
  RefreshCw, 
  Download,
  Eye
} from 'lucide-react';
import { api } from '../services/api';
import { KpiCard } from '../components/KpiCard';
import { ReceiptModal } from '../components/ReceiptModal';

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [recentTransactions, setRecentTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReceipt, setSelectedReceipt] = useState<any>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [kpiRes, trxRes] = await Promise.all([
        api.getDashboardKPIs(),
        api.getTransactions(1),
      ]);
      setData(kpiRes);
      setRecentTransactions(trxRes.transactions?.slice(0, 8) || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center p-20 text-slate-500">
        <RefreshCw className="w-8 h-8 animate-spin text-amber-500 mr-3" />
        <span className="font-medium">Loading live business analytics...</span>
      </div>
    );
  }

  const tm = data?.today_metrics || {};
  const ledger = data?.financial_ledger_summary || {};
  const status = data?.business_status || {};

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 to-slate-800 p-6 rounded-3xl text-white shadow-lg">
        <div>
          <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase tracking-wider mb-1">
            <span>Live Executive Overview</span>
            <span>•</span>
            <span>{status.timezone || 'Africa/Accra'}</span>
          </div>
          <h2 className="text-2xl font-black tracking-tight">Today's Financial Performance</h2>
          <p className="text-slate-400 text-sm mt-0.5">
            Strictly distinguishes completed sales from pending or unfulfilled customer orders.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchData}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-700/80 hover:bg-slate-700 text-white font-bold text-xs transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
          <a
            href="/api/admin/reports/export-csv"
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-xs shadow-md transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </a>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Today's Completed Sales"
          value={`GH₵ ${Number(tm.sales_volume || 0).toFixed(2)}`}
          subtitle={`${tm.order_count || 0} customer orders fulfilled`}
          icon={Banknote}
          badgeText="Completed"
          badgeColor="emerald"
          iconColor="text-emerald-600"
        />

        <KpiCard
          title="Estimated Net Profit"
          value={`GH₵ ${Number(ledger.estimated_net_profit || 0).toFixed(2)}`}
          subtitle="Net fee income + telco markup"
          icon={TrendingUp}
          badgeText="Real Profit"
          badgeColor="amber"
          iconColor="text-amber-600"
        />

        <KpiCard
          title="Airtime Sales Volume"
          value={`GH₵ ${Number(tm.airtime_sales || 0).toFixed(2)}`}
          subtitle="MTN, Telecel, AT airtime"
          icon={Smartphone}
          badgeText="Airtime"
          badgeColor="blue"
          iconColor="text-blue-600"
        />

        <KpiCard
          title="Data Bundle Volume"
          value={`GH₵ ${Number(tm.data_sales || 0).toFixed(2)}`}
          subtitle="Internet & non-expiry plans"
          icon={Wifi}
          badgeText="Data"
          badgeColor="purple"
          iconColor="text-purple-600"
        />
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="text-xs font-bold uppercase text-slate-500 mb-1">Provider Clearing Balance</div>
          <div className="text-xl font-extrabold text-slate-900">
            GH₵ {Number(ledger.provider_clearing_balance || 0).toFixed(2)}
          </div>
          <p className="text-xs text-slate-500 mt-1">Funds receivable across MTN MoMo / Hubtel</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="text-xs font-bold uppercase text-slate-500 mb-1">Agent Commissions Incurred</div>
          <div className="text-xl font-extrabold text-slate-900">
            GH₵ {Number(ledger.commission_expense || 0).toFixed(2)}
          </div>
          <p className="text-xs text-slate-500 mt-1">Paid or credited to POS cashiers</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="text-xs font-bold uppercase text-slate-500 mb-1">Transaction Health</div>
          <div className="flex items-center space-x-3 text-sm font-bold mt-1">
            <span className="text-emerald-600 flex items-center">
              <CheckCircle className="w-3.5 h-3.5 mr-1" />
              {tm.successful_transactions || 0} Success
            </span>
            <span className="text-amber-600 flex items-center">
              <Clock className="w-3.5 h-3.5 mr-1" />
              {tm.pending_transactions || 0} Pending
            </span>
            <span className="text-rose-600 flex items-center">
              <AlertCircle className="w-3.5 h-3.5 mr-1" />
              {tm.failed_transactions || 0} Failed
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Real-time status reconciliation active</p>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-extrabold text-slate-900 text-lg">Recent Ledger Transactions</h3>
            <p className="text-xs text-slate-500">Immutable double-entry payment movements in Ghana Cedis</p>
          </div>
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-slate-100 text-slate-700">
            {recentTransactions.length} Logged
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-50 text-[11px] uppercase font-bold text-slate-500 tracking-wider">
              <tr>
                <th className="px-6 py-3.5">Reference</th>
                <th className="px-6 py-3.5">Phone / Customer</th>
                <th className="px-6 py-3.5">Method</th>
                <th className="px-6 py-3.5">Amount (GHS)</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">Timestamp</th>
                <th className="px-6 py-3.5 text-right">Receipt</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {recentTransactions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400">
                    No transactions recorded yet. Use the MoMo Sandbox Test Bench to place test transactions.
                  </td>
                </tr>
              ) : (
                recentTransactions.map((trx) => (
                  <tr key={trx.id} className="hover:bg-slate-50/80 transition">
                    <td className="px-6 py-4 font-mono font-bold text-slate-900 text-xs">
                      {trx.transaction_reference}
                    </td>
                    <td className="px-6 py-4">{trx.customer_phone}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 rounded-md bg-slate-100 text-slate-800 text-xs font-semibold">
                        {trx.payment_method}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-extrabold text-slate-900">
                      GH₵ {Number(trx.amount).toFixed(2)}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${
                          trx.status === 'SUCCESSFUL'
                            ? 'bg-emerald-100 text-emerald-800'
                            : trx.status === 'PENDING'
                            ? 'bg-amber-100 text-amber-800 animate-pulse'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {trx.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">
                      {new Date(trx.created_at).toLocaleTimeString('en-GH', { timeZone: 'Africa/Accra' })}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {trx.status === 'SUCCESSFUL' && (
                        <button
                          onClick={() => setSelectedReceipt(trx)}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selectedReceipt && (
        <ReceiptModal transaction={selectedReceipt} onClose={() => setSelectedReceipt(null)} />
      )}
    </div>
  );
};
