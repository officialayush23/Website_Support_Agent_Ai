import React, { useEffect, useState, useMemo } from 'react';
import { apiRequest } from '../../../lib/api';
import { toast } from 'sonner';
import { 
  MapPin, Plus, Store, X, Package, 
  AlertTriangle, TrendingUp, Loader2, Clock, 
  ShoppingBag, CheckCircle 
} from 'lucide-react';

export default function AdminStores() {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Modal States
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedStore, setSelectedStore] = useState(null); 
  const [viewMode, setViewMode] = useState('inventory'); // 'inventory' | 'pickups' | 'hours'
  
  // Data for views
  const [storeInventory, setStoreInventory] = useState([]);
  const [storePickups, setStorePickups] = useState([]);
  const [loadingData, setLoadingData] = useState(false);

  // Form State
  const [newStore, setNewStore] = useState({ name: '', city: '', state: '', latitude: 0, longitude: 0 });

  useEffect(() => {
    fetchStores();
  }, []);

  const fetchStores = async () => {
    try {
      const data = await apiRequest('/stores/');
      setStores(data);
    } catch (err) {
      toast.error("Failed to fetch stores");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await apiRequest('/stores/admin', { method: 'POST', body: JSON.stringify(newStore) });
      toast.success("Store added");
      setShowAddModal(false);
      fetchStores();
      setNewStore({ name: '', city: '', state: '', latitude: 0, longitude: 0 });
    } catch (err) {
      toast.error("Failed to create store");
    }
  };

  // --- Handlers for Modal Views ---
  const openStoreModal = (store) => {
      setSelectedStore(store);
      setViewMode('inventory');
      fetchInventory(store.id);
  };

  const fetchInventory = async (storeId) => {
      setLoadingData(true);
      try {
          const data = await apiRequest(`/stores/${storeId}/inventory`);
          setStoreInventory(data.items || []);
      } catch (err) { toast.error("Failed to load inventory"); }
      finally { setLoadingData(false); }
  };

  const fetchPickups = async (storeId) => {
      setLoadingData(true);
      try {
          // Uses the specific Pickups router
          const data = await apiRequest(`/store/pickups/${storeId}`);
          setStorePickups(data);
      } catch (err) { toast.error("Failed to load pickups"); }
      finally { setLoadingData(false); }
  };

  const handleUpdatePickupStatus = async (pickupId, status) => {
      try {
          await apiRequest(`/store/pickups/${pickupId}?status=${status}`, { method: 'PATCH' });
          toast.success(`Pickup marked as ${status}`);
          fetchPickups(selectedStore.id); // Refresh
      } catch (err) {
          toast.error("Failed to update pickup");
      }
  };

  const handleTabChange = (mode) => {
      setViewMode(mode);
      if (mode === 'inventory') fetchInventory(selectedStore.id);
      if (mode === 'pickups') fetchPickups(selectedStore.id);
  };

  const stats = useMemo(() => {
      if (!storeInventory.length) return { totalStock: 0, lowStock: 0, value: 0 };
      return {
          totalItems: storeInventory.length,
          totalStock: storeInventory.reduce((acc, item) => acc + item.stock, 0),
          lowStock: storeInventory.filter(item => item.stock < 10).length,
      };
  }, [storeInventory]);

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
            <h1 className="text-2xl font-bold text-gray-900">Store Locations</h1>
            <p className="text-sm text-gray-500">Manage outlets, inventory & pickup orders.</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="bg-gray-900 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-gray-800 transition-colors shadow-lg">
          <Plus size={18} /> Add Store
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {stores.map(store => (
            <div key={store.id} onClick={() => openStoreModal(store)} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-start gap-4 cursor-pointer hover:border-blue-300 hover:shadow-md transition-all group">
                <div className="bg-indigo-50 p-3 rounded-lg text-indigo-600 group-hover:bg-indigo-100 transition-colors">
                    <Store size={24} />
                </div>
                <div>
                    <h3 className="font-bold text-gray-900">{store.name}</h3>
                    <div className="flex items-center gap-1 text-sm text-gray-500 mt-1">
                        <MapPin size={14} /> {store.city}, {store.state}
                    </div>
                    <div className="mt-3 flex gap-2">
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-500">Lat: {store.latitude}</span>
                        <span className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded font-medium">Manage →</span>
                    </div>
                </div>
            </div>
        ))}
      </div>

      {/* --- DETAIL MODAL --- */}
      {selectedStore && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl h-[85vh] flex flex-col animate-in zoom-in-95 overflow-hidden">
                
                {/* Header */}
                <div className="p-6 border-b border-gray-100 bg-gray-50/50">
                    <div className="flex justify-between items-center mb-4">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">{selectedStore.name}</h2>
                            <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                                <MapPin size={14} /> {selectedStore.city}, {selectedStore.state}
                            </div>
                        </div>
                        <button onClick={() => setSelectedStore(null)} className="p-2 hover:bg-gray-200 rounded-full transition-colors"><X size={20} /></button>
                    </div>
                    
                    {/* Tabs */}
                    <div className="flex gap-6 text-sm font-medium text-gray-500">
                        <button onClick={() => handleTabChange('inventory')} className={`pb-2 border-b-2 transition-colors ${viewMode === 'inventory' ? 'border-blue-600 text-blue-600' : 'border-transparent hover:text-gray-900'}`}>Inventory</button>
                        <button onClick={() => handleTabChange('pickups')} className={`pb-2 border-b-2 transition-colors ${viewMode === 'pickups' ? 'border-blue-600 text-blue-600' : 'border-transparent hover:text-gray-900'}`}>Pickup Orders</button>
                        <button onClick={() => handleTabChange('hours')} className={`pb-2 border-b-2 transition-colors ${viewMode === 'hours' ? 'border-blue-600 text-blue-600' : 'border-transparent hover:text-gray-900'}`}>Hours</button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 bg-white">
                    {loadingData ? (
                        <div className="h-full flex items-center justify-center"><Loader2 className="w-8 h-8 text-blue-500 animate-spin" /></div>
                    ) : (
                        <>
                            {viewMode === 'inventory' && (
                                <div className="space-y-8">
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                                            <div className="flex items-center gap-3 mb-2">
                                                <div className="p-2 bg-white rounded-lg text-blue-600"><Package size={18} /></div>
                                                <span className="text-sm font-medium text-blue-900">Total Stock</span>
                                            </div>
                                            <p className="text-2xl font-bold text-blue-700">{stats.totalStock}</p>
                                        </div>
                                        <div className="bg-green-50 p-4 rounded-xl border border-green-100">
                                            <div className="flex items-center gap-3 mb-2">
                                                <div className="p-2 bg-white rounded-lg text-green-600"><TrendingUp size={18} /></div>
                                                <span className="text-sm font-medium text-green-900">Unique Products</span>
                                            </div>
                                            <p className="text-2xl font-bold text-green-700">{stats.totalItems}</p>
                                        </div>
                                        <div className="bg-orange-50 p-4 rounded-xl border border-orange-100">
                                            <div className="flex items-center gap-3 mb-2">
                                                <div className="p-2 bg-white rounded-lg text-orange-600"><AlertTriangle size={18} /></div>
                                                <span className="text-sm font-medium text-orange-900">Low Stock</span>
                                            </div>
                                            <p className="text-2xl font-bold text-orange-700">{stats.lowStock}</p>
                                        </div>
                                    </div>

                                    <div className="border border-gray-200 rounded-xl overflow-hidden">
                                        <table className="min-w-full divide-y divide-gray-200">
                                            <thead className="bg-gray-50">
                                                <tr>
                                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Product</th>
                                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Stock</th>
                                                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase">Status</th>
                                                </tr>
                                            </thead>
                                            <tbody className="bg-white divide-y divide-gray-200">
                                                {storeInventory.map((item, idx) => (
                                                    <tr key={idx} className="hover:bg-gray-50">
                                                        <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.product_name}</td>
                                                        <td className="px-6 py-4 text-sm font-bold text-gray-900">{item.stock}</td>
                                                        <td className="px-6 py-4 text-right">
                                                            {item.stock === 0 ? <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">Out of Stock</span> : <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Healthy</span>}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}

                            {viewMode === 'pickups' && (
                                <div className="space-y-4">
                                    <h3 className="font-bold text-gray-900">Active Pickups</h3>
                                    {storePickups.length === 0 ? <p className="text-gray-500 border-2 border-dashed p-8 rounded-xl text-center">No active pickup requests.</p> : (
                                        storePickups.map(pickup => (
                                            <div key={pickup.id} className="p-4 border rounded-xl flex justify-between items-center hover:bg-gray-50 transition-colors">
                                                <div className="flex items-center gap-4">
                                                    <div className="bg-blue-50 p-2 rounded-lg text-blue-600"><ShoppingBag size={20} /></div>
                                                    <div>
                                                        <div className="flex items-center gap-2">
                                                            <p className="font-bold text-gray-900">Pickup #{pickup.id.slice(0,8)}</p>
                                                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full font-bold uppercase">{pickup.status}</span>
                                                        </div>
                                                        <p className="text-sm text-gray-500">Order: {pickup.order_id.slice(0,8)}</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-4">
                                                    {pickup.status === 'ready' && (
                                                        <button 
                                                            onClick={() => handleUpdatePickupStatus(pickup.id, 'picked_up')}
                                                            className="bg-gray-900 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-black transition-colors flex items-center gap-1"
                                                        >
                                                            <CheckCircle size={12} /> Mark as Picked Up
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            )}

                            {viewMode === 'hours' && (
                                <div className="text-center py-20 text-gray-500">
                                    <Clock className="mx-auto h-12 w-12 mb-4 opacity-20"/>
                                    <p className="text-lg">Working Hours Configuration</p>
                                    <p className="text-sm">Manage opening and closing times for this location.</p>
                                    <button className="mt-4 text-blue-600 font-medium hover:underline">Coming Soon</button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
          </div>
      )}

      {/* --- ADD STORE MODAL (Same as previous) --- */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg p-6 animate-in zoom-in-95">
                <h2 className="text-xl font-bold mb-4">Add Store Location</h2>
                <form onSubmit={handleCreate} className="space-y-4">
                    {/* ... form fields for new store ... */}
                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase">Store Name</label>
                        <input required className="w-full border rounded-lg p-2 mt-1" value={newStore.name} onChange={e => setNewStore({...newStore, name: e.target.value})} placeholder="Downtown Flagship" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <input placeholder="City" className="border p-2 rounded" value={newStore.city} onChange={e => setNewStore({...newStore, city: e.target.value})} />
                        <input placeholder="State" className="border p-2 rounded" value={newStore.state} onChange={e => setNewStore({...newStore, state: e.target.value})} />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <input placeholder="Latitude" type="number" step="any" className="border p-2 rounded" value={newStore.latitude} onChange={e => setNewStore({...newStore, latitude: parseFloat(e.target.value)})} />
                        <input placeholder="Longitude" type="number" step="any" className="border p-2 rounded" value={newStore.longitude} onChange={e => setNewStore({...newStore, longitude: parseFloat(e.target.value)})} />
                    </div>
                    <div className="flex justify-end gap-2 mt-6">
                        <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 text-gray-600">Cancel</button>
                        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg">Create</button>
                    </div>
                </form>
            </div>
        </div>
      )}
    </div>
  );
}