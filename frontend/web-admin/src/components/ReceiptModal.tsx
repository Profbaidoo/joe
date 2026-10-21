import React from 'react';
import { X, Printer, CheckCircle2, ShieldCheck, Share2 } from 'lucide-react';

interface ReceiptModalProps {
  transaction: any;
  onClose: () => void;
}

export const ReceiptModal: React.FC<ReceiptModalProps> = ({ transaction, onClose }) => {
  if (!transaction) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-slate-100 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="bg-gradient-to-r from-amber-500 to-yellow-400 p-6 text-slate-950 flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <span className="w-8 h-8 rounded-full bg-slate-950 text-amber-400 flex items-center justify-center font-bold text-sm">
                ₵
              </span>
              <span className="font-extrabold text-lg tracking-tight">Blessings Telecom</span>
            </div>
            <p className="text-xs font-semibold text-slate-900/80 mt-1">Official Digital Transaction Receipt</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-full bg-slate-950/10 hover:bg-slate-950/20 text-slate-950 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          <div className="text-center py-2 border-b border-dashed border-slate-200">
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 font-bold text-xs mb-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>PAYMENT SUCCESSFUL</span>
            </div>
            <div className="text-3xl font-black text-slate-900">
              GH₵ {Number(transaction.amount).toFixed(2)}
            </div>
            <p className="text-xs text-slate-500 mt-0.5">Currency: Ghana Cedis (GHS)</p>
          </div>

          <div className="space-y-3 text-sm">
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Transaction Ref</span>
              <span className="font-mono font-bold text-slate-900">{transaction.transaction_reference}</span>
            </div>

            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Service / Type</span>
              <span className="font-semibold text-slate-900">{transaction.payment_method || 'MoMo Collection'}</span>
            </div>

            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Customer Handset</span>
              <span className="font-semibold text-slate-900">{transaction.customer_phone}</span>
            </div>

            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Provider Clearing</span>
              <span className="font-semibold text-slate-900">{transaction.provider_name || 'MTN MoMo'}</span>
            </div>

            {transaction.external_id && (
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Financial Trans ID</span>
                <span className="font-mono text-xs text-slate-700">{transaction.external_id}</span>
              </div>
            )}

            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Date & Time</span>
              <span className="text-xs font-medium text-slate-700">
                {new Date(transaction.created_at).toLocaleString('en-GH', { timeZone: 'Africa/Accra' })} (Accra)
              </span>
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center text-xs text-slate-500 space-y-1">
            <div className="flex items-center justify-center space-x-1 font-bold text-slate-700">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Verified Append-Only Financial Ledger Record</span>
            </div>
            <p className="text-[11px]">Blessings Telecom & Financial Services Ltd. • Accra Central, Ghana</p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3 pt-2">
            <button
              onClick={handlePrint}
              className="flex-1 flex items-center justify-center space-x-2 py-2.5 rounded-xl bg-slate-900 text-white font-bold text-sm hover:bg-slate-800 transition"
            >
              <Printer className="w-4 h-4" />
              <span>Print Receipt</span>
            </button>
            <button
              onClick={onClose}
              className="px-5 py-2.5 rounded-xl border border-slate-300 font-bold text-sm text-slate-700 hover:bg-slate-50 transition"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
