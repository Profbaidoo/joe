import React, { useState } from 'react';
import { Send, CheckCircle2, AlertCircle, Clock, ShieldCheck, ArrowRight, RefreshCw, FileText } from 'lucide-react';
import { api } from '../services/api';
import { ReceiptModal } from '../components/ReceiptModal';

export const MomoTestBenchPage: React.FC = () => {
  const [phone, setPhone] = useState('0241234567');
  const [network, setNetwork] = useState('MTN');
  const [orderType, setOrderType] = useState('AIRTIME');
  const [amount, setAmount] = useState('10.00');
  const [loading, setLoading] = useState(false);
  const [reconciling, setReconciling] = useState(false);
  const [activeStep, setActiveStep] = useState<number>(1);
  const [activeOrder, setActiveOrder] = useState<any>(null);
  const [activeTrxRef, setActiveTrxRef] = useState<string | null>(null);
  const [resultMessage, setResultMessage] = useState<string | null>(null);
  const [reconciledTrx, setReconciledTrx] = useState<any>(null);
  const [showReceipt, setShowReceipt] = useState(false);

  const handleInitiatePayment = async () => {
    try {
      setLoading(true);
      setResultMessage(null);

      // Step 1: Create Order
      const orderRes = await api.createOrder({
        order_type: orderType,
        recipient_phone: phone,
        network_code: network,
        amount: parseFloat(amount),
      });

      const order = orderRes.order;
      setActiveOrder(order);

      // Step 2: Request MoMo Payment
      const payRes = await api.requestMoMoPayment(order.id, phone);
      setActiveTrxRef(payRes.transaction_reference);
      setResultMessage(payRes.message);
      setActiveStep(2);
    } catch (err: any) {
      alert(`Error initiating payment: ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReconcilePayment = async () => {
    if (!activeTrxRef) return;
    try {
      setReconciling(true);
      const res = await api.checkMoMoStatus(activeTrxRef);
      if (res.status === 'SUCCESSFUL') {
        setActiveStep(3);
        setResultMessage('Payment verified on MTN MoMo gateway! Order fulfilled and ledger updated.');
        setReconciledTrx({
          transaction_reference: activeTrxRef,
          customer_phone: phone,
          payment_method: `MOMO_${network}`,
          amount: parseFloat(amount),
          fee: 0.00,
          provider_name: 'MTN_MOMO',
          external_id: `MOMO-FIN-${Math.floor(100000 + Math.random() * 900000)}`,
          created_at: new Date().toISOString(),
        });
      } else {
        setResultMessage(`Current Status: ${res.status}. ${res.message || ''}`);
      }
    } catch (err: any) {
      alert(`Status query error: ${err.message || err}`);
    } finally {
      setReconciling(false);
    }
  };

  const handleReset = () => {
    setActiveStep(1);
    setActiveOrder(null);
    setActiveTrxRef(null);
    setResultMessage(null);
    setReconciledTrx(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">MTN MoMo Sandbox Test Bench</h2>
        <p className="text-xs text-slate-500">
          Simulate official MTN Mobile Money Collections API, customer push prompts, and status reconciliation.
        </p>
      </div>

      {/* Progress Steps */}
      <div className="grid grid-cols-3 gap-3 bg-white p-4 rounded-2xl border border-slate-200">
        <div className={`flex items-center space-x-2 text-xs font-bold ${activeStep >= 1 ? 'text-amber-600' : 'text-slate-400'}`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${activeStep >= 1 ? 'bg-amber-100 text-amber-800' : 'bg-slate-100'}`}>
            1
          </div>
          <span>Create & Prompt</span>
        </div>

        <div className={`flex items-center space-x-2 text-xs font-bold ${activeStep >= 2 ? 'text-amber-600' : 'text-slate-400'}`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${activeStep >= 2 ? 'bg-amber-100 text-amber-800' : 'bg-slate-100'}`}>
            2
          </div>
          <span>Handset Approval</span>
        </div>

        <div className={`flex items-center space-x-2 text-xs font-bold ${activeStep >= 3 ? 'text-emerald-600' : 'text-slate-400'}`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${activeStep >= 3 ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100'}`}>
            3
          </div>
          <span>Fulfilled & Ledgered</span>
        </div>
      </div>

      {/* Step 1: Form */}
      {activeStep === 1 && (
        <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
          <h3 className="font-extrabold text-slate-900 text-lg">Initiate MoMo Collection Prompt</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Customer Mobile Number</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="0241234567"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-amber-400"
              />
              <span className="text-[11px] text-slate-400 mt-1 block">Ghanaian prefix (024, 054, 020, 027...)</span>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Telecommunication Network</label>
              <select
                value={network}
                onChange={(e) => setNetwork(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-amber-400"
              >
                <option value="MTN">MTN Ghana</option>
                <option value="TELECEL">Telecel Ghana</option>
                <option value="AT">AT Ghana</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Service Type</label>
              <select
                value={orderType}
                onChange={(e) => setOrderType(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-amber-400"
              >
                <option value="AIRTIME">Airtime Top-up</option>
                <option value="MOMO_TRANSFER">Peer-to-Peer MoMo Transfer</option>
                <option value="UTILITY_BILL">Electricity (ECG) Bill</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Amount (GHS)</label>
              <div className="relative">
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 font-bold text-slate-400 text-sm">GH₵</span>
                <input
                  type="number"
                  step="0.50"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full pl-12 pr-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-amber-400"
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleInitiatePayment}
            disabled={loading}
            className="w-full py-3.5 rounded-2xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-black text-sm shadow-md flex items-center justify-center space-x-2 transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Dispatching Request-To-Pay...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Send MoMo Payment Request (GH₵ {amount})</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Step 2: Customer Handset Approval Simulation */}
      {activeStep === 2 && (
        <div className="bg-white rounded-3xl p-6 border border-amber-200 shadow-md space-y-5">
          <div className="flex items-center space-x-3 text-amber-600">
            <Clock className="w-6 h-6 animate-pulse" />
            <div>
              <h3 className="font-extrabold text-slate-900 text-lg">Awaiting Customer Approval</h3>
              <p className="text-xs text-slate-500">
                MTN MoMo API responded with HTTP 202 (Accepted). Prompt is waiting on subscriber's phone.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200/80 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Order Reference:</span>
              <span className="font-mono font-bold text-slate-900">{activeOrder?.order_reference}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Transaction Reference:</span>
              <span className="font-mono font-bold text-slate-900">{activeTrxRef}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Payer Handset:</span>
              <span className="font-bold text-slate-900">{phone}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Amount to Approve:</span>
              <span className="font-extrabold text-slate-900">GH₵ {amount}</span>
            </div>
          </div>

          {resultMessage && (
            <p className="text-xs font-semibold text-amber-800 bg-amber-100/60 p-3 rounded-xl border border-amber-200">
              {resultMessage}
            </p>
          )}

          <div className="flex items-center space-x-3 pt-2">
            <button
              onClick={handleReconcilePayment}
              disabled={reconciling}
              className="flex-1 py-3.5 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-black text-sm shadow-md flex items-center justify-center space-x-2 transition disabled:opacity-50"
            >
              {reconciling ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
                  <span>Polling MTN Gateway Status...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Simulate / Reconcile Customer Approval</span>
                </>
              )}
            </button>

            <button
              onClick={handleReset}
              className="px-5 py-3.5 rounded-2xl border border-slate-200 font-bold text-xs text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Success Screen */}
      {activeStep === 3 && (
        <div className="bg-white rounded-3xl p-6 border border-emerald-200 shadow-md space-y-5">
          <div className="text-center space-y-2 py-4">
            <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-2 shadow-inner">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-2xl font-black text-slate-900">Payment & Delivery Confirmed!</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              The customer approved the USSD prompt. The transaction has been recorded in the immutable financial ledger and telecom delivery dispatched.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200/80 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-600">Ledger Entry:</span>
              <span className="font-bold text-emerald-700">DOUBLE-ENTRY BALANCED</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Fulfillment Status:</span>
              <span className="font-bold text-emerald-700">FULFILLED (Airtime/Data Delivered)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">SMS Notification:</span>
              <span className="font-bold text-emerald-700">RECEIPT SMS SENT</span>
            </div>
          </div>

          <div className="flex items-center space-x-3 pt-2">
            <button
              onClick={() => setShowReceipt(true)}
              className="flex-1 py-3.5 rounded-2xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-black text-sm shadow flex items-center justify-center space-x-2 transition"
            >
              <FileText className="w-4 h-4" />
              <span>View Digital Receipt</span>
            </button>
            <button
              onClick={handleReset}
              className="px-6 py-3.5 rounded-2xl border border-slate-300 font-bold text-sm text-slate-700 hover:bg-slate-50"
            >
              Start New Test
            </button>
          </div>
        </div>
      )}

      {showReceipt && reconciledTrx && (
        <ReceiptModal transaction={reconciledTrx} onClose={() => setShowReceipt(false)} />
      )}
    </div>
  );
};
