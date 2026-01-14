import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiRequest } from '../../lib/api';
import { toast } from 'sonner';
import { Package, Truck, Check, Clock, MapPin, Loader2 } from 'lucide-react';

export default function OrderDetail() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [delivery, setDelivery] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [orderId]);

  const fetchData = async () => {
    try {
      // 1. Fetch Orders List (since we don't have GET /orders/{id} in user routers, we find it from list)
      // Ideally backend should have GET /orders/{id}
      const orders = await apiRequest('/orders/');
      const foundOrder = orders.find(o => o.id === orderId);
      
      if (foundOrder) {
          setOrder(foundOrder);
          // 2. Fetch Delivery Info
          try {
            const delData = await apiRequest(`/delivery/order/${orderId}`);
            setDelivery(delData);
          } catch (e) {
            // Delivery might not be created yet
          }
      }
    } catch (err) {
      toast.error("Failed to load order");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin text-gray-400" /></div>;
  if (!order) return <div className="p-10 text-center">Order not found</div>;

  const steps = [
      { id: 'pending', label: 'Order Placed', icon: Package },
      { id: 'paid', label: 'Processing', icon: Clock },
      { id: 'shipped', label: 'Shipped', icon: Truck },
      { id: 'delivered', label: 'Delivered', icon: Check }
  ];

  const currentStepIdx = steps.findIndex(s => s.id === order.status) || 0;

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in duration-500">
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Order #{order.id.slice(0,8)}</h1>
                    <p className="text-gray-500">Placed on {new Date(order.created_at).toLocaleDateString()}</p>
                </div>
                <div className="text-right">
                    <p className="text-xl font-bold text-gray-900">${order.total}</p>
                    <span className="inline-block px-3 py-1 bg-gray-100 rounded-full text-xs font-bold uppercase mt-1">{order.status}</span>
                </div>
            </div>

            {/* Tracking Steps */}
            <div className="relative flex justify-between mb-12">
                {/* Progress Bar Background */}
                <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-100 -z-10 -translate-y-1/2 rounded-full"></div>
                {/* Active Progress Bar */}
                <div 
                    className="absolute top-1/2 left-0 h-1 bg-green-500 -z-10 -translate-y-1/2 rounded-full transition-all duration-700" 
                    style={{ width: `${(currentStepIdx / (steps.length - 1)) * 100}%` }}
                ></div>

                {steps.map((step, idx) => {
                    const isActive = idx <= currentStepIdx;
                    return (
                        <div key={step.id} className="flex flex-col items-center gap-2 bg-white px-2">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-colors ${isActive ? 'bg-green-500 border-green-500 text-white' : 'bg-white border-gray-300 text-gray-300'}`}>
                                <step.icon size={14} />
                            </div>
                            <span className={`text-xs font-medium ${isActive ? 'text-gray-900' : 'text-gray-400'}`}>{step.label}</span>
                        </div>
                    );
                })}
            </div>

            {/* Delivery Info */}
            {delivery && (
                <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 flex items-start gap-4">
                    <div className="bg-white p-2 rounded-lg text-blue-600"><Truck size={20} /></div>
                    <div>
                        <h3 className="font-bold text-blue-900">Delivery Update</h3>
                        <p className="text-sm text-blue-700 mt-1">
                            Courier: <span className="font-medium">{delivery.courier || 'Pending'}</span> 
                            {delivery.tracking_id && ` • Tracking: ${delivery.tracking_id}`}
                        </p>
                        <p className="text-xs text-blue-500 mt-1 uppercase font-bold tracking-wider">{delivery.status.replace(/_/g, ' ')}</p>
                    </div>
                </div>
            )}
        </div>
    </div>
  );
}