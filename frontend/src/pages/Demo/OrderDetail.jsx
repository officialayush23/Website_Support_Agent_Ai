import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { toast } from 'sonner';
import { 
    Package, Truck, Check, Clock, MapPin, Loader2, XCircle, 
    RefreshCcw, MessageSquare, AlertTriangle, ArrowLeft 
} from 'lucide-react';

export default function OrderDetail() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [delivery, setDelivery] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Modals
  const [refundModal, setRefundModal] = useState(false);
  const [complaintModal, setComplaintModal] = useState(false);
  const [reason, setReason] = useState('');

  useEffect(() => {
    fetchData();
  }, [orderId]);

  const fetchData = async () => {
    try {
      // 1. Fetch Order List & Find specific order (Since GET /orders/{id} is missing in user router)
      const orders = await apiRequest('/orders/');
      const foundOrder = orders.find(o => o.id === orderId);
      
      if (foundOrder) {
          setOrder(foundOrder);
          // 2. Fetch Delivery Info (Graceful fail if not exists)
          try {
            const delData = await apiRequest(`/delivery/order/${orderId}`);
            setDelivery(delData);
          } catch (e) {}
      } else {
          toast.error("Order not found");
          navigate('/demo/orders');
      }
    } catch (err) {
      toast.error("Failed to load order details");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
      if(!confirm("Are you sure you want to cancel this order?")) return;
      try {
          await apiRequest(`/orders/${orderId}/cancel`, { method: 'PATCH' });
          toast.success("Order cancelled");
          fetchData(); // Refresh status
      } catch (err) {
          toast.error("Failed to cancel order");
      }
  };

  const submitRefund = async () => {
      try {
          await apiRequest('/refunds/', {
              method: 'POST',
              body: JSON.stringify({ order_id: orderId, reason })
          });
          toast.success("Refund requested successfully");
          setRefundModal(false);
          setReason('');
      } catch (err) {
          toast.error("Failed to request refund");
      }
  };

  const submitComplaint = async () => {
      // Assuming you have a complaint endpoint, otherwise redirects to chat
      // If no direct complaint endpoint in the list provided, we use Support Chat
      navigate('/demo/chat', { state: { context: `Complaint regarding Order #${orderId.slice(0,8)}: ${reason}` } });
  };

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin text-gray-400" /></div>;
  if (!order) return null;

  const steps = [
      { id: 'pending', label: 'Placed', icon: Package },
      { id: 'paid', label: 'Processing', icon: Clock },
      { id: 'shipped', label: 'Shipped', icon: Truck },
      { id: 'delivered', label: 'Delivered', icon: Check }
  ];

  const currentStepIdx = steps.findIndex(s => s.id === order.status) || 0;
  const isCancelled = order.status === 'cancelled';

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in duration-500">
        <button onClick={() => navigate('/demo/orders')} className="flex items-center text-gray-500 hover:text-gray-900 mb-4">
            <ArrowLeft size={16} className="mr-1" /> Back to Orders
        </button>

        {/* Header Card */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm relative overflow-hidden">
            <div className="flex justify-between items-start mb-8 relative z-10">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        Order #{order.id.slice(0,8)}
                        {isCancelled && <span className="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full">Cancelled</span>}
                    </h1>
                    <p className="text-gray-500 text-sm mt-1">Placed on {new Date(order.created_at).toLocaleDateString()}</p>
                </div>
                <div className="text-right">
                    <p className="text-2xl font-bold text-gray-900">${order.total}</p>
                    <p className="text-sm text-gray-500">{order.items?.length} items</p>
                </div>
            </div>

            {/* Tracking Steps (Hide if cancelled) */}
            {!isCancelled && (
                <div className="relative flex justify-between mb-8">
                    <div className="absolute top-4 left-0 w-full h-1 bg-gray-100 -z-10 rounded-full"></div>
                    <div 
                        className="absolute top-4 left-0 h-1 bg-green-500 -z-10 rounded-full transition-all duration-700" 
                        style={{ width: `${(currentStepIdx / (steps.length - 1)) * 100}%` }}
                    ></div>

                    {steps.map((step, idx) => {
                        const isActive = idx <= currentStepIdx;
                        return (
                            <div key={step.id} className="flex flex-col items-center gap-2 bg-white px-2">
                                <div className={`w-9 h-9 rounded-full flex items-center justify-center border-2 transition-colors ${isActive ? 'bg-green-500 border-green-500 text-white' : 'bg-white border-gray-200 text-gray-300'}`}>
                                    <step.icon size={14} />
                                </div>
                                <span className={`text-xs font-medium ${isActive ? 'text-gray-900' : 'text-gray-400'}`}>{step.label}</span>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 border-t border-gray-100 pt-6">
                {order.status === 'pending' && (
                    <button onClick={handleCancel} className="px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors flex items-center gap-2">
                        <XCircle size={16} /> Cancel Order
                    </button>
                )}
                {order.status === 'delivered' && (
                    <button onClick={() => setRefundModal(true)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors flex items-center gap-2">
                        <RefreshCcw size={16} /> Request Refund
                    </button>
                )}
                <button onClick={() => setComplaintModal(true)} className="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center gap-2 ml-auto">
                    <MessageSquare size={16} /> Need Help?
                </button>
            </div>
        </div>

        {/* Delivery Details */}
        {delivery && (
            <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 flex items-start gap-4">
                <div className="bg-white p-3 rounded-xl text-blue-600 shadow-sm"><Truck size={24} /></div>
                <div>
                    <h3 className="font-bold text-blue-900">Delivery Status</h3>
                    <p className="text-sm text-blue-700 mt-1">
                        Courier: <span className="font-medium">{delivery.courier || 'Pending'}</span> 
                        {delivery.tracking_id && ` • Tracking: ${delivery.tracking_id}`}
                    </p>
                    <p className="text-xs text-blue-500 mt-2 uppercase font-bold tracking-wider">{delivery.status.replace(/_/g, ' ')}</p>
                </div>
            </div>
        )}

        {/* Order Items */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                <h3 className="font-semibold text-gray-900">Items Ordered</h3>
            </div>
            <div className="divide-y divide-gray-100">
                {order.items?.map((item, idx) => (
                    <div key={idx} className="p-6 flex justify-between items-center">
                        <div>
                            <p className="font-medium text-gray-900">Product ID: {item.product_id.slice(0,8)}...</p>
                            <p className="text-sm text-gray-500">Qty: {item.quantity} x ${item.price}</p>
                        </div>
                        <p className="font-bold text-gray-900">${(item.quantity * item.price).toFixed(2)}</p>
                    </div>
                ))}
            </div>
            <div className="p-6 bg-gray-50 flex justify-between items-center border-t border-gray-200">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-bold text-gray-900">${order.subtotal}</span>
            </div>
            {order.discount_total > 0 && (
                <div className="px-6 py-2 bg-green-50 flex justify-between items-center text-green-700 text-sm">
                    <span>Discount Applied</span>
                    <span>-${order.discount_total}</span>
                </div>
            )}
        </div>

        {/* --- MODALS --- */}
        {refundModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4 backdrop-blur-sm">
                <div className="bg-white p-6 rounded-xl w-full max-w-md shadow-2xl">
                    <h2 className="text-xl font-bold mb-4">Request Refund</h2>
                    <textarea 
                        className="w-full border rounded-lg p-3 h-32 mb-4 focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="Reason for refund..."
                        value={reason}
                        onChange={e => setReason(e.target.value)}
                    />
                    <div className="flex justify-end gap-2">
                        <button onClick={() => setRefundModal(false)} className="px-4 py-2 text-gray-600">Cancel</button>
                        <button onClick={submitRefund} className="px-4 py-2 bg-black text-white rounded-lg">Submit Request</button>
                    </div>
                </div>
            </div>
        )}

        {complaintModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4 backdrop-blur-sm">
                <div className="bg-white p-6 rounded-xl w-full max-w-md shadow-2xl">
                    <h2 className="text-xl font-bold mb-2 flex items-center gap-2">
                        <AlertTriangle className="text-orange-500"/> File Complaint
                    </h2>
                    <p className="text-sm text-gray-500 mb-4">Describe your issue. We will open a support chat context.</p>
                    <textarea 
                        className="w-full border rounded-lg p-3 h-32 mb-4 focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="What went wrong?"
                        value={reason}
                        onChange={e => setReason(e.target.value)}
                    />
                    <div className="flex justify-end gap-2">
                        <button onClick={() => setComplaintModal(false)} className="px-4 py-2 text-gray-600">Cancel</button>
                        <button onClick={submitComplaint} className="px-4 py-2 bg-blue-600 text-white rounded-lg">Start Chat</button>
                    </div>
                </div>
            </div>
        )}
    </div>
  );
}