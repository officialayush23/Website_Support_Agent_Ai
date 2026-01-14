import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { toast } from 'sonner';
import { Package, Truck, Check, X, Clock } from 'lucide-react';

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const data = await apiRequest('/orders/');
      setOrders(data);
    } catch (err) {
      toast.error("Failed to fetch orders");
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
      switch(status) {
          case 'delivered': return <Check className="text-green-500" />;
          case 'cancelled': return <X className="text-red-500" />;
          case 'shipped': return <Truck className="text-blue-500" />;
          default: return <Clock className="text-orange-500" />;
      }
  };

  if (loading) return <div className="p-10 text-center">Loading orders...</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500">
      <h1 className="text-3xl font-bold text-gray-900" style={{ fontFamily: '"Charm", cursive' }}>Order History</h1>

      {orders.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-gray-200">
              <p className="text-gray-500">You haven't placed any orders yet.</p>
          </div>
      ) : (
          orders.map(order => (
              <div key={order.id} className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:border-blue-200 transition-colors">
                  <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-4">
                          <div className="p-3 bg-gray-50 rounded-full">
                              {getStatusIcon(order.status)}
                          </div>
                          <div>
                              <h3 className="font-bold text-gray-900 text-lg">Order #{order.id.slice(0,8)}</h3>
                              <p className="text-sm text-gray-500">{new Date(order.created_at).toLocaleDateString()} at {new Date(order.created_at).toLocaleTimeString()}</p>
                          </div>
                      </div>
                      <div className="text-right">
                          <p className="text-2xl font-bold text-gray-900">${order.total}</p>
                          <span className="inline-block px-3 py-1 rounded-full text-xs font-bold uppercase bg-gray-100 text-gray-600 mt-1">
                              {order.status}
                          </span>
                      </div>
                  </div>

                  {/* If you have order items in the response, map them here. 
                      Based on your schema OrderOut, it currently only has total/status. 
                      You might want to update OrderOut to include items: List[OrderItemOut] 
                  */}
                  
                  <div className="border-t border-gray-100 pt-4 flex justify-between items-center">
                      <p className="text-sm text-gray-500">Items: {order.items?.length || 0}</p>
                      {/* Placeholder for future "Track Package" button if delivery exists */}
                  </div>
              </div>
          ))
      )}
    </div>
  );
}