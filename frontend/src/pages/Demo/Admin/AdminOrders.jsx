import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { 
    Package, Truck, CheckCircle, XCircle, 
    MoreHorizontal, Filter, Eye 
} from 'lucide-react';
import { toast } from 'sonner';

const STATUS_COLORS = {
    pending: 'bg-yellow-100 text-yellow-700',
    paid: 'bg-blue-100 text-blue-700',
    shipped: 'bg-purple-100 text-purple-700',
    delivered: 'bg-green-100 text-green-700',
    cancelled: 'bg-red-100 text-red-700',
};

export default function AdminOrders() {
    const [orders, setOrders] = useState([]);
    const [filter, setFilter] = useState('all');
    const [selectedOrder, setSelectedOrder] = useState(null);

    useEffect(() => { loadOrders(); }, []);

    const loadOrders = async () => {
        try {
            const data = await apiRequest('/orders/'); // Assuming endpoint exists or we use admin specific
            setOrders(data);
        } catch (e) { toast.error("Failed to load orders"); }
    };

    const filteredOrders = filter === 'all' ? orders : orders.filter(o => o.status === filter);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold dark:text-white">Order Management</h1>
                <div className="flex gap-2">
                    {['all', 'pending', 'shipped'].map(f => (
                        <button 
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-3 py-1.5 rounded-lg text-sm capitalize ${filter === f ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
                <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 dark:bg-gray-900 border-b border-gray-100 dark:border-gray-700">
                        <tr>
                            <th className="p-4 font-medium text-gray-500">Order ID</th>
                            <th className="p-4 font-medium text-gray-500">Customer</th>
                            <th className="p-4 font-medium text-gray-500">Total</th>
                            <th className="p-4 font-medium text-gray-500">Status</th>
                            <th className="p-4 font-medium text-gray-500">Date</th>
                            <th className="p-4 font-medium text-gray-500">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                        {filteredOrders.map(order => (
                            <tr key={order.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                <td className="p-4 font-mono text-xs text-gray-500">#{order.id.substring(0,8)}</td>
                                <td className="p-4 font-medium dark:text-white">User {order.user_id.substring(0,4)}</td>
                                <td className="p-4 dark:text-white">₹{order.total}</td>
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-700'}`}>
                                        {order.status}
                                    </span>
                                </td>
                                <td className="p-4 text-gray-500">{new Date(order.created_at).toLocaleDateString()}</td>
                                <td className="p-4">
                                    <button 
                                        onClick={() => setSelectedOrder(order)}
                                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-500"
                                    >
                                        <Eye size={16} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Order Detail Modal */}
            {selectedOrder && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                    <div className="bg-white dark:bg-gray-800 w-full max-w-2xl rounded-xl shadow-xl overflow-hidden">
                        <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between">
                            <h2 className="text-xl font-bold dark:text-white">Order Details</h2>
                            <button onClick={() => setSelectedOrder(null)}><XCircle className="text-gray-400" /></button>
                        </div>
                        <div className="p-6 space-y-6">
                            <div className="flex justify-between items-center bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                                <div>
                                    <p className="text-sm text-gray-500">Status</p>
                                    <p className="font-bold text-lg capitalize dark:text-white">{selectedOrder.status}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm text-gray-500">Total Amount</p>
                                    <p className="font-bold text-lg text-green-600">₹{selectedOrder.total}</p>
                                </div>
                            </div>
                            
                            {/* Items List (Mocked for now as list endpoint might not return items) */}
                            <div>
                                <h3 className="font-semibold mb-2 dark:text-white">Items</h3>
                                <div className="space-y-2">
                                    {selectedOrder.items?.map((item, i) => (
                                        <div key={i} className="flex justify-between text-sm border-b border-gray-100 dark:border-gray-700 pb-2">
                                            <span className="dark:text-gray-300">Product Variant {item.variant_id.substring(0,6)}</span>
                                            <span className="font-mono">x{item.quantity}</span>
                                        </div>
                                    )) || <p className="text-sm text-gray-400">Items data not loaded in summary.</p>}
                                </div>
                            </div>
                        </div>
                        <div className="p-6 bg-gray-50 dark:bg-gray-900 flex justify-end gap-2">
                            <button className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-100 dark:border-gray-700 dark:text-white dark:hover:bg-gray-800">Refund</button>
                            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">Update Status</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}