import React from 'react';
import { LayoutDashboard, ReceiptText, Smartphone, Users, Activity, FileText, Send } from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  userRole?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab, userRole }) => {
  const navItems = [
    { id: 'dashboard', label: 'Financial Dashboard', icon: LayoutDashboard },
    { id: 'transactions', label: 'Transactions & Receipts', icon: ReceiptText },
    { id: 'products', label: 'Products & Pricing', icon: Smartphone },
    { id: 'agents', label: 'Agents & Cashiers', icon: Users },
    { id: 'momo-sandbox', label: 'MoMo Sandbox Test', icon: Send },
    { id: 'audit', label: 'Security & Audit Logs', icon: Activity },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 min-h-[calc(100vh-65px)] p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Core Operations
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-sm transition-all ${
                isActive
                  ? 'bg-amber-400 text-slate-950 font-bold shadow-md'
                  : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-slate-950' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3 text-xs space-y-1.5">
        <div className="font-bold text-white flex items-center justify-between">
          <span>Active Telcos</span>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        </div>
        <div className="flex items-center space-x-2 text-[11px]">
          <span className="px-1.5 py-0.5 rounded bg-yellow-400/20 text-yellow-300 font-bold">MTN</span>
          <span className="px-1.5 py-0.5 rounded bg-red-400/20 text-red-300 font-bold">Telecel</span>
          <span className="px-1.5 py-0.5 rounded bg-blue-400/20 text-blue-300 font-bold">AT</span>
        </div>
        <p className="text-[10px] text-slate-400 pt-1">
          Sandbox Mode Active
        </p>
      </div>
    </aside>
  );
};
