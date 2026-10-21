import React from 'react';
import { LogOut, ShieldCheck, Clock, Phone } from 'lucide-react';
import { clearAuthTokens } from '../services/api';

interface NavbarProps {
  user: any;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ user, onLogout }) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 px-6 py-3.5 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-yellow-400 flex items-center justify-center font-bold text-slate-950 text-xl shadow-md">
          ₵
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-extrabold text-slate-900 tracking-tight text-lg">Blessings Telecom</h1>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
              GHANA FINTECH
            </span>
          </div>
          <p className="text-xs text-slate-500">Mobile Money, Airtime & Data Management Portal</p>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        <div className="hidden md:flex items-center space-x-2 text-xs font-medium text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>Africa/Accra (GMT)</span>
        </div>

        <div className="flex items-center space-x-3 border-l pl-6 border-slate-200">
          <div className="text-right">
            <div className="text-sm font-bold text-slate-900 flex items-center justify-end space-x-1">
              <span>{user?.username || 'Admin'}</span>
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-xs text-slate-500 font-medium">Role: {user?.role || 'ADMIN'}</div>
          </div>

          <button
            onClick={() => {
              clearAuthTokens();
              onLogout();
            }}
            className="p-2 rounded-lg text-slate-500 hover:text-red-600 hover:bg-red-50 transition"
            title="Sign Out"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
};
