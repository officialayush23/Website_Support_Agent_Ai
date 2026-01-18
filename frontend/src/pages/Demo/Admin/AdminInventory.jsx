import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { toast } from 'sonner';
import { Box, TrendingUp, AlertTriangle, Search, Save, Loader2 } from 'lucide-react';

export default function AdminInventory() {
  const [stats, setStats] = useState({ total_value: 0, total_items: 0, low_stock_variants: 0 });
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    Promise.all([
        apiRequest('/admin/inventory/stats'),
        apiRequest('/stores/admin/catalog')
    ]).then(([s, c]) => {
        setStats(s);
        setCatalog(c);
        setLoading(false);
    }).catch(() => toast.error("Failed to load inventory"));
  }, []);

  const updateGlobal = async (variantId, val) => {
      try {
          await apiRequest('/stores/admin/global-stock', {
              method: 'PATCH',
              body: JSON.stringify({ variant_id: variantId, total_stock: parseInt(val) })
          });
          toast.success("Updated");
      } catch (e) { toast.error("Failed"); }
  };

  if(loading) return <div className="p-20 text-center"><Loader2 className="animate-spin mx-auto"/></div>;

  return (
    <div className="space-y-8">
        <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: '"Charm", cursive' }}>Global Inventory</h1>
        
        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-black text-white p-6 rounded-xl shadow-lg">
                <p className="text-gray-400 font-medium text-sm">Total Asset Value</p>
                <h3 className="text-3xl font-bold mt-1">₹{stats.total_value.toLocaleString()}</h3>
                <TrendingUp className="mt-4 text-green-400" />
            </div>
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <p className="text-gray-500 font-medium text-sm">Total Units</p>
                <h3 className="text-3xl font-bold mt-1">{stats.total_items}</h3>
                <Box className="mt-4 text-gray-300" />
            </div>
            <div className="bg-white p-6 rounded-xl border border-red-100 shadow-sm">
                <p className="text-red-500 font-medium text-sm">Low Stock Alerts</p>
                <h3 className="text-3xl font-bold mt-1 text-red-600">{stats.low_stock_variants}</h3>
                <AlertTriangle className="mt-4 text-red-200" />
            </div>
        </div>

        {/* Catalog Table */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="p-4 border-b flex gap-4 bg-gray-50">
                <Search className="text-gray-400" />
                <input 
                    placeholder="Search SKU or Product..." 
                    className="flex-1 outline-none bg-transparent"
                    onChange={e => setSearch(e.target.value)}
                />
            </div>
            <table className="w-full text-left text-sm">
                <thead className="bg-gray-50 text-gray-500 font-medium">
                    <tr><th className="p-4">SKU</th><th className="p-4">Price</th><th className="p-4">Global Total</th><th className="p-4">Allocated</th><th className="p-4">Reserved</th></tr>
                </thead>
                <tbody className="divide-y">
                    {catalog.filter(i => i.sku.toLowerCase().includes(search.toLowerCase())).map(item => (
                        <tr key={item.variant_id} className="hover:bg-gray-50">
                            <td className="p-4 font-mono font-medium">{item.sku}</td>
                            <td className="p-4">₹{item.price}</td>
                            <td className="p-4">
                                <div className="flex items-center gap-2">
                                    <input 
                                        type="number" 
                                        defaultValue={item.total_stock}
                                        className="w-20 p-1 border rounded text-center focus:ring-1 focus:ring-black outline-none"
                                        onBlur={(e) => updateGlobal(item.variant_id, e.target.value)}
                                    />
                                </div>
                            </td>
                            <td className="p-4 font-bold text-blue-600">{item.allocated_stock}</td>
                            <td className="p-4 font-bold text-orange-600">{item.reserved_stock}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    </div>
  );
}