import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../../lib/api';
import { Package, MapPin, Calendar, CreditCard, ArrowLeft, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function OrderDetail() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const data = await api.get(`/orders/${orderId}`);
        setOrder(data);
      } catch (err) {
        toast.error("Order not found");
        navigate('/demo/orders');
      } finally {
        setLoading(false);
      }
    };
    fetchOrder();
  }, [orderId, navigate]);

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin"/></div>;
  if (!order) return null;

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in">
       <button onClick={() => navigate('/demo/orders')} className="text-gray-500 hover:text-gray-900 flex items-center gap-2 text-sm"><ArrowLeft size={16}/> Back to Orders</button>
       
       <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-8 border-b border-gray-100 bg-gray-50/50 flex justify-between items-start">
             <div>
               <h1 className="text-2xl font-bold text-gray-900">Order #{order.id.slice(0,8)}</h1>
               <p className="text-gray-500 mt-1 flex items-center gap-2"><Calendar size={14}/> {new Date(order.created_at).toLocaleString()}</p>
             </div>
             <div className="text-right">
               <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold uppercase ${order.status === 'delivered' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>{order.status}</span>
             </div>
          </div>

          <div className="p-8 grid md:grid-cols-2 gap-8">
             <div>
                <h3 className="text-sm font-bold text-gray-900 uppercase mb-4">Items</h3>
                <div className="space-y-4">
                   {order.items?.map(item => (
                     <div key={item.id} className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">{item.variant?.product?.name || "Product"} (x{item.quantity})</span>
                        <span className="font-medium">${item.price}</span>
                     </div>
                   ))}
                </div>
                <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between font-bold text-lg">
                   <span>Total</span>
                   <span>${order.total}</span>
                </div>
             </div>

             <div className="space-y-6">
                <div>
                   <h3 className="text-sm font-bold text-gray-900 uppercase mb-2 flex items-center gap-2"><MapPin size={16}/> Shipping</h3>
                   {order.address ? (
                     <p className="text-gray-600 text-sm">{order.address.address_line1}, {order.address.city}, {order.address.pincode}</p>
                   ) : <p className="text-gray-500 italic">Store Pickup</p>}
                </div>
                <div>
                   <h3 className="text-sm font-bold text-gray-900 uppercase mb-2 flex items-center gap-2"><CreditCard size={16}/> Payment</h3>
                   <p className="text-gray-600 text-sm">Paid via Card</p>
                </div>
             </div>
          </div>
       </div>
    </div>
  );
}