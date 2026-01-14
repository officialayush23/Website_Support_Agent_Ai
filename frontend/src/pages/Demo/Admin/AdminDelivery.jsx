import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { toast } from 'sonner';
import { Truck, MapPin, Package, Edit2, Loader2, Save } from 'lucide-react';

export default function AdminDelivery() {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Edit State
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    fetchDeliveries();
  }, []);

  const fetchDeliveries = async () => {
    try {
      // Calls the new GET /delivery/admin endpoint
      const data = await apiRequest('/delivery/admin');
      setDeliveries(data);
    } catch (err) {
      toast.error("Failed to load deliveries");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (del) => {
      setEditingId(del.id);
      setFormData({ 
          courier: del.courier || '', 
          tracking_id: del.tracking_id || '', 
          status: del.status 
      });
  };

  const handleSave = async (id) => {
      try {
          await apiRequest(`/delivery/admin/${id}`, {
              method: 'PATCH',
              body: JSON.stringify(formData)
          });
          
          setDeliveries(prev => prev.map(d => d.id === id ? { ...d, ...formData } : d));
          setEditingId(null);
          toast.success("Logistics updated");
      } catch (err) {
          toast.error("Update failed");
      }
  };

  if (loading) return <div className="flex justify-center p-10"><Loader2 className="animate-spin text-gray-400" /></div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <h1 className="text-2xl font-bold text-gray-900">Logistics & Delivery</h1>

      <div className="grid gap-4">
          {deliveries.length === 0 ? <p className="text-gray-500 text-center py-8">No active deliveries.</p> : deliveries.map(del => (
              <div key={del.id} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                  <div className="flex justify-between items-start">
                      <div className="flex items-center gap-3">
                          <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600"><Truck size={20} /></div>
                          <div>
                              <h3 className="font-semibold text-gray-900">Order #{del.order_id?.slice(0,8)}</h3>
                              <p className="text-xs text-gray-500 uppercase tracking-wider">{new Date(del.created_at).toLocaleDateString()}</p>
                          </div>
                      </div>
                      <button onClick={() => handleEdit(del)} className="text-gray-400 hover:text-blue-600 p-2"><Edit2 size={16} /></button>
                  </div>

                  {editingId === del.id ? (
                      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg animate-in slide-in-from-top-2">
                          <div>
                              <label className="text-xs font-semibold text-gray-500 uppercase">Courier</label>
                              <input className="w-full p-2 rounded border border-gray-300 text-sm mt-1" value={formData.courier} onChange={e => setFormData({...formData, courier: e.target.value})} placeholder="e.g. DHL" />
                          </div>
                          <div>
                              <label className="text-xs font-semibold text-gray-500 uppercase">Tracking ID</label>
                              <input className="w-full p-2 rounded border border-gray-300 text-sm mt-1" value={formData.tracking_id} onChange={e => setFormData({...formData, tracking_id: e.target.value})} placeholder="Tracking #" />
                          </div>
                          <div>
                              <label className="text-xs font-semibold text-gray-500 uppercase">Status</label>
                              <select className="w-full p-2 rounded border border-gray-300 text-sm mt-1" value={formData.status} onChange={e => setFormData({...formData, status: e.target.value})}>
                                  <option value="pending">Pending</option>
                                  <option value="assigned">Assigned</option>
                                  <option value="out_for_delivery">Out for Delivery</option>
                                  <option value="delivered">Delivered</option>
                                  <option value="failed">Failed</option>
                              </select>
                          </div>
                          <div className="md:col-span-3 flex justify-end gap-2 mt-2">
                              <button onClick={() => setEditingId(null)} className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900">Cancel</button>
                              <button onClick={() => handleSave(del.id)} className="px-4 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2">
                                <Save size={14}/> Save
                              </button>
                          </div>
                      </div>
                  ) : (
                      <div className="mt-4 flex flex-wrap gap-6 text-sm text-gray-600">
                          <div className="flex items-center gap-2"><Package size={16} className="text-gray-400" /> {del.courier || 'Unassigned'}</div>
                          <div className="flex items-center gap-2"><MapPin size={16} className="text-gray-400" /> {del.tracking_id || 'No Tracking'}</div>
                          <div className="flex items-center gap-2">
                              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${del.status === 'delivered' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                                  {del.status?.replace(/_/g, ' ').toUpperCase()}
                              </span>
                          </div>
                      </div>
                  )}
              </div>
          ))}
      </div>
    </div>
  );
}