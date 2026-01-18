import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { MapPin, Plus, Layers, Search, Store as StoreIcon, CheckCircle, X } from 'lucide-react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { toast } from 'sonner';
import L from 'leaflet';

// Leaflet Icon Fix
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function LocationPicker({ setLocation }) {
    useMapEvents({ click(e) { setLocation({ lat: e.latlng.lat, lng: e.latlng.lng }); } });
    return null;
}

export default function AdminStores() {
    const [stores, setStores] = useState([]);
    const [view, setView] = useState('list');
    const [selectedStore, setSelectedStore] = useState(null);
    const [formData, setFormData] = useState({ name: '', city: '', state: '', lat: 20.5937, lng: 78.9629 });

    useEffect(() => { loadStores(); }, []);
    const loadStores = async () => { setStores(await apiRequest('/stores/')); };

    const handleCreate = async () => {
        try {
            await apiRequest('/stores/admin', {
                method: 'POST',
                body: JSON.stringify({
                    name: formData.name, city: formData.city, state: formData.state,
                    latitude: formData.lat, longitude: formData.lng
                })
            });
            toast.success("Store Created");
            setView('list'); loadStores();
        } catch (err) { toast.error("Failed"); }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight" style={{ fontFamily: '"Charm", cursive' }}>Store Locations</h1>
                {view === 'list' ? (
                    <button onClick={() => setView('create')} className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">
                        <Plus size={18} /> Add Store
                    </button>
                ) : (
                    <button onClick={() => setView('list')} className="text-gray-500 hover:text-black">Cancel</button>
                )}
            </div>

            {view === 'list' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {stores.map(store => (
                        <div 
                            key={store.id} 
                            onClick={() => setSelectedStore(store)}
                            className="bg-white p-6 rounded-xl border border-gray-200 cursor-pointer hover:border-black hover:shadow-lg transition-all group"
                        >
                            <div className="flex justify-between mb-4">
                                <div className="p-3 bg-gray-50 rounded-lg group-hover:bg-black group-hover:text-white transition-colors">
                                    <StoreIcon size={24}/>
                                </div>
                                <span className={`px-2 py-1 rounded text-xs h-fit font-medium ${store.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                    {store.is_active ? 'Active' : 'Closed'}
                                </span>
                            </div>
                            <h3 className="font-bold text-lg">{store.name}</h3>
                            <p className="text-gray-500 text-sm">{store.city}, {store.state}</p>
                        </div>
                    ))}
                </div>
            )}

            {view === 'create' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="space-y-4 bg-white p-6 rounded-xl border border-gray-200">
                        <input className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-black outline-none" placeholder="Store Name" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                        <div className="grid grid-cols-2 gap-4">
                            <input className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-black outline-none" placeholder="City" value={formData.city} onChange={e => setFormData({...formData, city: e.target.value})} />
                            <input className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-black outline-none" placeholder="State" value={formData.state} onChange={e => setFormData({...formData, state: e.target.value})} />
                        </div>
                        <button onClick={handleCreate} className="w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-gray-800">Create Store</button>
                    </div>
                    <div className="h-[400px] rounded-xl overflow-hidden border border-gray-200 relative">
                        <MapContainer center={[formData.lat, formData.lng]} zoom={5} style={{ height: '100%', width: '100%' }}>
                            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                            <Marker position={[formData.lat, formData.lng]} />
                            <LocationPicker setLocation={loc => setFormData({...formData, ...loc})} />
                        </MapContainer>
                        <div className="absolute bottom-4 left-4 bg-white/90 px-3 py-1 rounded text-xs font-medium z-[1000] shadow-sm">
                            Click map to pin location
                        </div>
                    </div>
                </div>
            )}

            {/* Store Dashboard Popover */}
            {selectedStore && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                    <div className="bg-white w-full max-w-4xl h-[80vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-in zoom-in-95">
                        <div className="p-6 border-b flex justify-between items-center bg-gray-50">
                            <div>
                                <h2 className="text-2xl font-bold font-charm" style={{ fontFamily: '"Charm", cursive' }}>{selectedStore.name}</h2>
                                <p className="text-sm text-gray-500">{selectedStore.city} • Dashboard</p>
                            </div>
                            <button onClick={() => setSelectedStore(null)} className="p-2 hover:bg-gray-200 rounded-full"><X /></button>
                        </div>
                        <div className="flex-1 overflow-y-auto p-0">
                            <StoreDashboardTabs store={selectedStore} />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function StoreDashboardTabs({ store }) {
    const [tab, setTab] = useState('inventory');
    const [inventory, setInventory] = useState([]);
    const [pickups, setPickups] = useState([]);
    const [search, setSearch] = useState('');

    useEffect(() => {
        if(tab === 'inventory') apiRequest(`/stores/${store.id}/inventory`).then(res => setInventory(res.items));
        if(tab === 'pickups') apiRequest(`/pickups/store/${store.id}`).then(setPickups);
    }, [tab, store.id]);

    const handleAllocate = async (variantId, qty) => {
        try {
            await apiRequest(`/stores/${store.id}/allocate`, {
                method: 'POST',
                body: JSON.stringify({ variant_id: variantId, quantity: parseInt(qty) })
            });
            toast.success("Allocated!");
            // Refresh
            apiRequest(`/stores/${store.id}/inventory`).then(res => setInventory(res.items));
        } catch (e) { toast.error("Allocation Failed"); }
    };

    const handlePickupStatus = async (id, status) => {
        try {
            await apiRequest(`/pickups/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) });
            toast.success("Updated");
            setPickups(prev => prev.map(p => p.id === id ? { ...p, status } : p));
        } catch (e) { toast.error("Failed"); }
    };

    return (
        <div>
            <div className="flex border-b">
                <button onClick={() => setTab('inventory')} className={`flex-1 py-4 text-sm font-medium ${tab === 'inventory' ? 'border-b-2 border-black text-black' : 'text-gray-500'}`}>Inventory Allocation</button>
                <button onClick={() => setTab('pickups')} className={`flex-1 py-4 text-sm font-medium ${tab === 'pickups' ? 'border-b-2 border-black text-black' : 'text-gray-500'}`}>Pickups & Orders</button>
            </div>

            <div className="p-6">
                {tab === 'inventory' && (
                    <>
                        <div className="mb-4 relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
                            <input 
                                placeholder="Search SKU..." 
                                className="w-full pl-10 p-2 border rounded-lg focus:ring-1 focus:ring-black outline-none"
                                value={search} onChange={e => setSearch(e.target.value)}
                            />
                        </div>
                        <table className="w-full text-left text-sm">
                            <thead className="bg-gray-50 text-gray-500">
                                <tr><th className="p-3 rounded-l-lg">SKU</th><th className="p-3">In Store</th><th className="p-3">Allocated</th><th className="p-3 rounded-r-lg">Allocate (+/-)</th></tr>
                            </thead>
                            <tbody className="divide-y">
                                {inventory.filter(i => i.sku.toLowerCase().includes(search.toLowerCase())).map(item => (
                                    <tr key={item.variant_id}>
                                        <td className="p-3 font-mono">{item.sku}</td>
                                        <td className="p-3 font-bold text-green-600">{item.in_hand_stock}</td>
                                        <td className="p-3">{item.allocated_stock}</td>
                                        <td className="p-3">
                                            <input 
                                                type="number" 
                                                placeholder="0" 
                                                className="w-20 p-1 border rounded text-center focus:ring-1 focus:ring-black outline-none"
                                                onKeyDown={(e) => { if(e.key === 'Enter') { handleAllocate(item.variant_id, e.target.value); e.target.value = ''; } }}
                                            />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </>
                )}

                {tab === 'pickups' && (
                    <div className="space-y-3">
                        {pickups.map(p => (
                            <div key={p.id} className="flex justify-between items-center p-4 border rounded-xl hover:bg-gray-50">
                                <div>
                                    <p className="font-bold">Order #{p.order_id.slice(0,8)}</p>
                                    <p className="text-xs text-gray-500">₹{p.amount} • {new Date(p.created_at).toLocaleDateString()}</p>
                                </div>
                                <div className="flex gap-2">
                                    {p.status === 'ready' && (
                                        <button onClick={() => handlePickupStatus(p.id, 'picked_up')} className="bg-black text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-gray-800">
                                            Mark Picked Up
                                        </button>
                                    )}
                                    <span className={`px-2 py-1 rounded text-xs border ${p.status === 'picked_up' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-gray-100 border-gray-200'}`}>
                                        {p.status}
                                    </span>
                                </div>
                            </div>
                        ))}
                        {pickups.length === 0 && <p className="text-center text-gray-400 py-10">No active pickups</p>}
                    </div>
                )}
            </div>
        </div>
    );
}