import React, { useEffect, useState } from 'react';
import { api, getAuthToken } from './services/api';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { ProductsPage } from './pages/ProductsPage';
import { AgentsPage } from './pages/AgentsPage';
import { MomoTestBenchPage } from './pages/MomoTestBenchPage';
import { AuditPage } from './pages/AuditPage';
import { LoginPage } from './pages/LoginPage';
import { RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      api.getProfile()
        .then((res) => setUser(res.user))
        .catch(() => setUser(null))
        .finally(() => setCheckingAuth(false));
    } else {
      setCheckingAuth(false);
    }
  }, []);

  if (checkingAuth) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-300">
        <RefreshCw className="w-8 h-8 animate-spin text-amber-400 mr-3" />
        <span className="font-bold">Verifying security session...</span>
      </div>
    );
  }

  if (!user) {
    return <LoginPage onLoginSuccess={(u) => setUser(u)} />;
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar user={user} onLogout={() => setUser(null)} />

      <div className="flex flex-1">
        <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} userRole={user.role} />

        <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full">
          {currentTab === 'dashboard' && <DashboardPage />}
          {currentTab === 'transactions' && <TransactionsPage />}
          {currentTab === 'products' && <ProductsPage />}
          {currentTab === 'agents' && <AgentsPage />}
          {currentTab === 'momo-sandbox' && <MomoTestBenchPage />}
          {currentTab === 'audit' && <AuditPage />}
        </main>
      </div>
    </div>
  );
};

export default App;
