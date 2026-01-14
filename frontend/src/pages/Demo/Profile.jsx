import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { useAuth } from '../../context/AuthContext';
import { toast } from 'sonner';
import { 
  Package, MapPin, User, Settings, CheckCircle, 
  XCircle, Plus, Trash2, MessageSquare, RefreshCcw, Star, Sliders, AlertTriangle
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Profile() {
  const { user, profile } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('orders');
  
  // Data States
  const [orders, setOrders] = useState([]);
  const [addresses, setAddresses] = useState([]);
  const [preferences, setPreferences] = useState(null);
  const [refunds, setRefunds] = useState([]);
  
  // Modal States
  const [refundModal, setRefundModal] = useState({ open: false, orderId: null });
  const [addressModal, setAddressModal] = useState(false);
  const [refundReason, setRefundReason] = useState('');
  
  // New Address Form
  const [newAddress, setNewAddress] = useState({
    label: 'Home', address_line1: '', address_line2: '', city: '', state: '', pincode: '', country: 'India', is_default: false
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [ordersData, addressesData, prefsData, refundsData] = await Promise.all([
        apiRequest('/orders/'),
        apiRequest('/addresses/'),
        apiRequest('/users/me/preferences'),
        apiRequest('/refunds/me')
      ]);
      setOrders(ordersData);
      setAddresses(addressesData);
      setPreferences(prefsData);
      setRefunds(refundsData);
    } catch (err) {
      toast.error("Failed to load profile data");
    }
  };

  // --- ACTIONS ---

  const handleAddAddress = async (e) => {
    e.preventDefault();
    try {
        const payload = {
            label: newAddress.label,
            address_line1: newAddress.address_line1,
            address_line2: newAddress.address_line2 || null,
            city: newAddress.city,
            state: newAddress.state,
            pincode: String(newAddress.pincode),
            country: 'India',
            is_default: newAddress.is_default
        };
        await apiRequest('/addresses/', { method: 'POST', body: JSON.stringify(payload) });
        toast.success("Address added");
        setAddressModal(false);
        fetchData();
        setNewAddress({ label: 'Home', address_line1: '', address_line2: '', city: '', state: '', pincode: '', country: 'India', is_default: false });
    } catch (err) { toast.error("Failed to add address"); }
  };

  const handleSetDefault = async (id) => {
      try {
          await apiRequest(`/addresses/${id}/default`, { method: 'PATCH' });
          toast.success("Default address updated");
          fetchData();
      } catch (err) { toast.error("Failed to update default"); }
  };

  const handleDeleteAddress = async (id) => {
      if(!confirm("Delete this address?")) return;
      try {
          await apiRequest(`/addresses/${id}`, { method: 'DELETE' });
          setAddresses(prev => prev.filter(a => a.id !== id));
          toast.success("Address deleted");
      } catch (err) { toast.error("Failed to delete"); }
  };

  const handleCancelOrder = async (orderId) => {
    if(!confirm("Cancel this order?")) return;
    try {
        await apiRequest(`/orders/${orderId}/cancel`, { method: 'PATCH' });
        toast.success("Order cancelled");
        fetchData(); 
    } catch (err) { toast.error("Failed to cancel order"); }
  };

  const handleRequestRefund = async (e) => {
    e.preventDefault();
    try {
        await apiRequest('/refunds/', { method: 'POST', body: JSON.stringify({ order_id: refundModal.orderId, reason: refundReason }) });
        toast.success("Refund requested");
        setRefundModal({ open: false, orderId: null });
        setRefundReason('');
        fetchData();
    } catch (err) { toast.error("Refund request failed"); }
  };

  const handleSupportChat = async (orderId) => {
      // Start a conversation with context about this order
      navigate('/demo/chat', { state: { context: `Issue with Order #${orderId.slice(0,8)}` } });
  };

  // Analytics Stats
  const totalSpent = orders.reduce((acc, o) => acc + (o.status !== 'cancelled' ? o.total : 0), 0);
  const activeOrders = orders.filter(o => ['pending', 'paid', 'shipped'].includes(o.status)).length;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Header Profile Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 bg-white rounded-2xl p-8 border border-gray-200 shadow-sm flex flex-col sm:flex-row items-center gap-6">
            <div className="h-24 w-24 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                {profile?.name?.[0] || user?.email?.[0]?.toUpperCase()}
            </div>
            <div className="text-center sm:text-left flex-1">
                <h1 className="text-3xl font-bold text-gray-900">{profile?.name || "Valued Customer"}</h1>
                <p className="text-gray-500">{user?.email}</p>
                <div className="mt-4 flex gap-2 justify-center sm:justify-start">
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gray-100 text-xs text-gray-600 font-medium border border-gray-200">
                        <User size={14} /> {profile?.role === 'admin' ? 'Administrator' : 'Member'}
                    </span>
                </div>
            </div>
          </div>

          {/* Quick Analytics */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm flex flex-col justify-center space-y-4">
              <div className="flex justify-between items-center">
                  <span className="text-gray-500 text-sm">Total Orders</span>
                  <span className="font-bold text-xl">{orders.length}</span>
              </div>
              <div className="flex justify-between items-center">
                  <span className="text-gray-500 text-sm">Active Orders</span>
                  <span className="font-bold text-xl text-blue-600">{activeOrders}</span>
              </div>
              <div className="flex justify-between items-center border-t border-gray-100 pt-4">
                  <span className="text-gray-500 text-sm">Total Spent</span>
                  <span className="font-bold text-xl text-green-600">${totalSpent.toFixed(2)}</span>
              </div>
          </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Nav */}
          <div className="lg:col-span-1 space-y-2">
              {[
                  {id: 'orders', label: 'My Orders', icon: Package},
                  {id: 'addresses', label: 'Addresses', icon: MapPin},
                  {id: 'settings', label: 'Settings', icon: Settings},
                  {id: 'refunds', label: 'Refund Requests', icon: RefreshCcw}
              ].map(tab => (
                  <button 
                    key={tab.id} 
                    onClick={() => setActiveTab(tab.id)} 
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${activeTab === tab.id ? 'bg-gray-900 text-white shadow-md' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                  >
                      <tab.icon size={18} /> {tab.label}
                  </button>
              ))}
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
              
              {/* --- ORDERS TAB --- */}
              {activeTab === 'orders' && (
                  <div className="space-y-4">
                      {orders.length === 0 ? (
                          <div className="bg-white p-12 rounded-2xl text-center border border-dashed border-gray-300">
                              <Package className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                              <p className="text-gray-500 mb-4">No orders yet.</p>
                              <button onClick={() => navigate('/demo')} className="bg-blue-600 text-white px-6 py-2 rounded-lg">Shop Now</button>
                          </div>
                      ) : orders.map(order => (
                          <div key={order.id} className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-all">
                              <div className="flex justify-between items-start mb-4">
                                  <div>
                                      <div className="flex items-center gap-3">
                                          <h3 className="font-bold text-gray-900">Order #{order.id.slice(0,8)}</h3>
                                          <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                                              order.status === 'delivered' ? 'bg-green-100 text-green-700' : 
                                              order.status === 'cancelled' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                                          }`}>{order.status}</span>
                                      </div>
                                      <p className="text-sm text-gray-500 mt-1">{new Date(order.created_at).toLocaleDateString()} • {order.items?.length || 0} Items</p>
                                  </div>
                                  <p className="text-xl font-bold text-gray-900">${order.total}</p>
                              </div>
                              
                              <div className="flex flex-wrap gap-2 justify-end border-t border-gray-100 pt-4">
                                  {order.status === 'pending' && (
                                      <button onClick={() => handleCancelOrder(order.id)} className="px-3 py-1.5 text-sm text-red-600 bg-red-50 hover:bg-red-100 rounded-lg flex items-center gap-2">
                                          <XCircle size={14} /> Cancel
                                      </button>
                                  )}
                                  {(order.status === 'delivered' || order.status === 'paid') && (
                                      <button onClick={() => setRefundModal({ open: true, orderId: order.id })} className="px-3 py-1.5 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center gap-2">
                                          <RefreshCcw size={14} /> Refund
                                      </button>
                                  )}
                                  <button onClick={() => handleSupportChat(order.id)} className="px-3 py-1.5 text-sm text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg flex items-center gap-2">
                                      <MessageSquare size={14} /> Complaint / Help
                                  </button>
                              </div>
                          </div>
                      ))}
                  </div>
              )}

              {/* --- REFUNDS TAB --- */}
              {activeTab === 'refunds' && (
                  <div className="space-y-4">
                      {refunds.length === 0 ? (
                          <p className="text-gray-500 text-center py-10 bg-white rounded-xl border border-gray-200">No refund requests found.</p>
                      ) : refunds.map(refund => (
                          <div key={refund.id} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex justify-between items-center">
                              <div>
                                  <div className="flex items-center gap-2 mb-1">
                                      <span className="font-bold text-gray-900">Order #{refund.order_id.slice(0,8)}</span>
                                      <span className={`text-xs px-2 py-0.5 rounded font-bold uppercase ${
                                          refund.status === 'approved' ? 'bg-green-100 text-green-700' :
                                          refund.status === 'rejected' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                                      }`}>{refund.status}</span>
                                  </div>
                                  <p className="text-sm text-gray-500">Reason: {refund.reason}</p>
                              </div>
                              <div className="text-right text-xs text-gray-400">
                                  {new Date(refund.created_at).toLocaleDateString()}
                              </div>
                          </div>
                      ))}
                  </div>
              )}

              {/* --- ADDRESSES TAB --- */}
              {activeTab === 'addresses' && (
                  <div className="space-y-4">
                      <div className="flex justify-between items-center mb-4">
                          <h2 className="text-xl font-bold text-gray-900">Saved Addresses</h2>
                          <button onClick={() => setAddressModal(true)} className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-lg"><Plus size={16} /> Add New</button>
                      </div>
                      <div className="grid md:grid-cols-2 gap-4">
                          {addresses.map(addr => (
                              <div key={addr.id} className="bg-white p-5 rounded-xl border border-gray-200 relative group hover:border-blue-300 transition-all">
                                  <div className="flex justify-between items-start mb-2">
                                      <div className="flex gap-2">
                                        <span className="bg-gray-100 text-gray-600 text-xs font-bold uppercase px-2 py-1 rounded inline-block">{addr.label}</span>
                                        {addr.is_default && <span className="bg-blue-100 text-blue-600 text-xs font-bold uppercase px-2 py-1 rounded inline-block">Default</span>}
                                      </div>
                                      <button onClick={() => handleDeleteAddress(addr.id)} className="text-gray-400 hover:text-red-500"><Trash2 size={16} /></button>
                                  </div>
                                  <p className="text-gray-900 font-medium">{addr.address_line1}</p>
                                  <p className="text-gray-500 text-sm">{addr.city}, {addr.state} - {addr.pincode}</p>
                                  
                                  {!addr.is_default && (
                                      <button onClick={() => handleSetDefault(addr.id)} className="mt-3 text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1">
                                          <Star size={12} /> Set as Default
                                      </button>
                                  )}
                              </div>
                          ))}
                      </div>
                  </div>
              )}

              {/* --- SETTINGS TAB --- */}
              {activeTab === 'settings' && (
                  <div className="bg-white p-8 rounded-xl border border-gray-200">
                      <h2 className="text-xl font-bold text-gray-900 mb-6">Account Settings</h2>
                      
                      <div className="space-y-4 mb-8">
                          <div><label className="block text-sm font-medium text-gray-700">Full Name</label><input disabled className="mt-1 w-full p-2 border rounded-lg bg-gray-50 text-gray-500" value={profile?.name || ''} /></div>
                          <div><label className="block text-sm font-medium text-gray-700">Email Address</label><input disabled className="mt-1 w-full p-2 border rounded-lg bg-gray-50 text-gray-500" value={user?.email || ''} /></div>
                      </div>

                      <div className="border-t border-gray-100 pt-6">
                          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2"><Sliders size={18} /> User Preferences</h3>
                          {preferences ? (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  {Object.entries(preferences).map(([key, value]) => (
                                      <div key={key} className="p-4 bg-gray-50 rounded-xl border border-gray-100 flex justify-between items-center">
                                          <span className="text-sm font-medium text-gray-700 capitalize">{key.replace(/_/g, ' ')}</span>
                                          <span className="text-sm font-semibold text-gray-900 bg-white px-3 py-1 rounded shadow-sm border border-gray-200">
                                              {typeof value === 'boolean' ? (value ? 'Enabled' : 'Disabled') : String(value)}
                                          </span>
                                      </div>
                                  ))}
                              </div>
                          ) : <p className="text-gray-500 italic">No specific preferences found.</p>}
                      </div>
                  </div>
              )}
          </div>
      </div>

      {/* --- MODALS --- */}
      {refundModal.open && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm">
              <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 animate-in zoom-in-95">
                  <h2 className="text-xl font-bold mb-4">Request Refund</h2>
                  <textarea className="w-full border rounded-lg p-3 h-32 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Reason for refund..." value={refundReason} onChange={e => setRefundReason(e.target.value)} />
                  <div className="flex justify-end gap-2 mt-6">
                      <button onClick={() => setRefundModal({open:false, orderId:null})} className="px-4 py-2 text-gray-600">Cancel</button>
                      <button onClick={handleRequestRefund} className="px-4 py-2 bg-black text-white rounded-lg">Submit</button>
                  </div>
              </div>
          </div>
      )}

      {addressModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm">
              <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg p-6 animate-in zoom-in-95 overflow-y-auto max-h-[90vh]">
                  <h2 className="text-xl font-bold mb-4">Add New Address</h2>
                  <form onSubmit={handleAddAddress} className="space-y-4">
                      {/* ...Address Form Inputs... */}
                      {/* (Using the corrected form from previous steps) */}
                      <div><label className="block text-xs font-bold text-gray-500 uppercase">Label</label><input required className="w-full border rounded-lg p-2 mt-1" value={newAddress.label} onChange={e => setNewAddress({...newAddress, label: e.target.value})} placeholder="Home, Work..." /></div>
                      <div><label className="block text-xs font-bold text-gray-500 uppercase">Address Line 1</label><input required className="w-full border rounded-lg p-2 mt-1" value={newAddress.address_line1} onChange={e => setNewAddress({...newAddress, address_line1: e.target.value})} /></div>
                      <div><label className="block text-xs font-bold text-gray-500 uppercase">Address Line 2</label><input className="w-full border rounded-lg p-2 mt-1" value={newAddress.address_line2} onChange={e => setNewAddress({...newAddress, address_line2: e.target.value})} /></div>
                      <div className="grid grid-cols-2 gap-4">
                          <div><label className="block text-xs font-bold text-gray-500 uppercase">City</label><input required className="w-full border rounded-lg p-2 mt-1" value={newAddress.city} onChange={e => setNewAddress({...newAddress, city: e.target.value})} /></div>
                          <div><label className="block text-xs font-bold text-gray-500 uppercase">State</label><input required className="w-full border rounded-lg p-2 mt-1" value={newAddress.state} onChange={e => setNewAddress({...newAddress, state: e.target.value})} /></div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                          <div><label className="block text-xs font-bold text-gray-500 uppercase">Pincode</label><input required type="text" className="w-full border rounded-lg p-2 mt-1" value={newAddress.pincode} onChange={e => setNewAddress({...newAddress, pincode: e.target.value})} /></div>
                          <div><label className="block text-xs font-bold text-gray-500 uppercase">Country</label><input disabled className="w-full border rounded-lg p-2 mt-1 bg-gray-50" value="India" /></div>
                      </div>
                      <div className="flex items-center gap-2"><input type="checkbox" checked={newAddress.is_default} onChange={e => setNewAddress({...newAddress, is_default: e.target.checked})} className="rounded border-gray-300" /><label className="text-sm text-gray-700">Set as default address</label></div>
                      <div className="flex justify-end gap-2 mt-6">
                          <button type="button" onClick={() => setAddressModal(false)} className="px-4 py-2 text-gray-600">Cancel</button>
                          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg">Save Address</button>
                      </div>
                  </form>
              </div>
          </div>
      )}
    </div>
  );
}