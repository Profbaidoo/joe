import React, { useEffect, useState } from 'react';
import { Smartphone, Wifi, Save, Check, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export const ProductsPage: React.FC = () => {
  const [products, setProducts] = useState<any[]>([]);
  const [bundles, setBundles] = useState<any[]>([]);
  const [selectedNetwork, setSelectedNetwork] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [saveSuccessId, setSaveSuccessId] = useState<number | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [prodRes, bundleRes] = await Promise.all([
        api.getProducts(),
        api.getDataBundles(),
      ]);
      setProducts(prodRes.products || []);
      setBundles(bundleRes.data_bundles || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handlePriceUpdate = async (productId: number, retailPrice: number, wholesalePrice: number) => {
    try {
      setSavingId(productId);
      await api.updatePricing(productId, {
        retail_price: retailPrice,
        wholesale_price: wholesalePrice,
      });
      setSaveSuccessId(productId);
      setTimeout(() => setSaveSuccessId(null), 2000);
      fetchData();
    } catch (err) {
      alert(`Error updating price: ${err}`);
    } finally {
      setSavingId(null);
    }
  };

  const filteredBundles = bundles.filter((b) =>
    selectedNetwork === 'ALL' ? true : b.network_code === selectedNetwork
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Products & Pricing Management</h2>
          <p className="text-xs text-slate-500">
            Configure retail prices, wholesale costs, and profit margins for Ghanaian telecom services.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="flex items-center space-x-1.5 px-3 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold transition w-fit"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Catalog</span>
        </button>
      </div>

      {/* Network Filter Pills */}
      <div className="flex items-center space-x-2 bg-white p-2 rounded-2xl border border-slate-200 w-fit">
        {['ALL', 'MTN', 'TELECEL', 'AT'].map((net) => (
          <button
            key={net}
            onClick={() => setSelectedNetwork(net)}
            className={`px-4 py-1.5 rounded-xl text-xs font-bold transition ${
              selectedNetwork === net
                ? 'bg-slate-900 text-white shadow-sm'
                : 'hover:bg-slate-100 text-slate-600'
            }`}
          >
            {net === 'ALL' ? 'All Networks' : net}
          </button>
        ))}
      </div>

      {/* Airtime Rate Cards */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden p-6 space-y-4">
        <div className="flex items-center space-x-2">
          <Smartphone className="w-5 h-5 text-amber-500" />
          <h3 className="font-extrabold text-slate-900 text-lg">Airtime Distribution Products</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {products
            .filter((p) => p.category === 'AIRTIME')
            .filter((p) => (selectedNetwork === 'ALL' ? true : p.network_code === selectedNetwork))
            .map((p) => {
              const margin = (((p.retail_price - p.wholesale_price) / p.retail_price) * 100).toFixed(1);
              return (
                <div key={p.id} className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-extrabold text-slate-900">{p.name}</span>
                    <span className="px-2 py-0.5 rounded-md bg-amber-100 text-amber-900 text-xs font-bold">
                      {p.network_code}
                    </span>
                  </div>

                  <div className="space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Wholesale Rate:</span>
                      <span className="font-bold text-slate-700">{(p.wholesale_price * 100).toFixed(0)}% of face value</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Retail Rate:</span>
                      <span className="font-bold text-slate-700">{(p.retail_price * 100).toFixed(0)}% of face value</span>
                    </div>
                    <div className="flex justify-between pt-1 border-t border-slate-200">
                      <span className="text-slate-500">Net Telco Margin:</span>
                      <span className="font-black text-emerald-600">+{margin}%</span>
                    </div>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Data Bundle Packages */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Wifi className="w-5 h-5 text-indigo-500" />
            <h3 className="font-extrabold text-slate-900 text-lg">Internet Data Bundle Catalog</h3>
          </div>
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-slate-100 text-slate-700">
            {filteredBundles.length} Plans Active
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-50 text-[11px] uppercase font-bold text-slate-500 tracking-wider">
              <tr>
                <th className="px-6 py-3.5">Network</th>
                <th className="px-6 py-3.5">Plan Name</th>
                <th className="px-6 py-3.5">Volume</th>
                <th className="px-6 py-3.5">Validity</th>
                <th className="px-6 py-3.5">Wholesale Cost (GHS)</th>
                <th className="px-6 py-3.5">Selling Price (GHS)</th>
                <th className="px-6 py-3.5">Gross Margin</th>
                <th className="px-6 py-3.5 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filteredBundles.map((b) => {
                const marginAmount = (b.retail_price - b.wholesale_price).toFixed(2);
                const marginPct = (((b.retail_price - b.wholesale_price) / b.retail_price) * 100).toFixed(1);
                return (
                  <tr key={b.id} className="hover:bg-slate-50/80 transition">
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded font-black text-xs bg-slate-100 text-slate-900">
                        {b.network_code}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-bold text-slate-900">{b.name}</td>
                    <td className="px-6 py-4">
                      <span className="font-extrabold text-indigo-600">
                        {b.volume_mb >= 1024 ? `${(b.volume_mb / 1024).toFixed(1)} GB` : `${b.volume_mb} MB`}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs font-semibold text-slate-600">
                      {b.validity_days === 0 ? (
                        <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Non-Expiry
                        </span>
                      ) : (
                        `${b.validity_days} Days`
                      )}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-600">
                      GH₵ {Number(b.wholesale_price).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 font-black text-slate-900">
                      GH₵ {Number(b.retail_price).toFixed(2)}
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                        +GH₵ {marginAmount} ({marginPct}%)
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                        Active
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
