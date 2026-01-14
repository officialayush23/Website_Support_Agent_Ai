import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { toast } from 'sonner';
import { DollarSign, XCircle, CheckCircle, Loader2 } from 'lucide-react';

export default function AdminRefunds() {
  const [refunds, setRefunds] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRefunds();
  }, []);

  const fetchRefunds = async () => {
    try {
      // Calls the new GET /refunds/admin endpoint
      const data = await apiRequest('/refunds/admin');
      setRefunds(data);
    } catch (err) {
      toast.error("Failed to fetch refunds");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRefund = async (id, newStatus) => {
    try {
      await apiRequest(`/refunds/${id}?status=${newStatus}`, { method: 'PATCH' });
      setRefunds(prev => prev.map(r => r.id === id ? { ...r, status: newStatus } : r));
      toast.success(`Refund ${newStatus}`);
    } catch (err) {
      toast.error("Failed to update refund");
    }
  };

  if (loading) return <div className="flex justify-center p-10"><Loader2 className="animate-spin text-gray-400" /></div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Refund Requests</h1>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
                <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
                {refunds.length === 0 ? (
                    <tr><td colSpan="5" className="text-center py-4 text-gray-500">No active refund requests</td></tr>
                ) : (
                    refunds.map(refund => (
                        <tr key={refund.id}>
                            <td className="px-6 py-4 text-sm font-medium text-gray-900">#{refund.order_id?.slice(0,8)}</td>
                            <td className="px-6 py-4 text-sm text-gray-500">{refund.reason || 'No reason provided'}</td>
                            {/* Assuming amount is fetched or we just show N/A if not in list view yet */}
                            <td className="px-6 py-4 text-sm font-bold text-gray-900">{refund.amount ? `$${refund.amount}` : 'N/A'}</td>
                            <td className="px-6 py-4">
                                <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium 
                                    ${refund.status === 'approved' ? 'bg-green-100 text-green-800' : 
                                      refund.status === 'rejected' ? 'bg-red-100 text-red-800' : 
                                      'bg-blue-100 text-blue-800'}`}>
                                    {refund.status.toUpperCase()}
                                </span>
                            </td>
                            <td className="px-6 py-4 text-right">
                                {refund.status === 'initiated' && (
                                    <div className="flex justify-end gap-2">
                                        <button onClick={() => handleUpdateRefund(refund.id, 'rejected')} className="p-1 text-red-600 hover:bg-red-50 rounded" title="Reject"><XCircle size={18} /></button>
                                        <button onClick={() => handleUpdateRefund(refund.id, 'approved')} className="p-1 text-green-600 hover:bg-green-50 rounded" title="Approve"><CheckCircle size={18} /></button>
                                    </div>
                                )}
                            </td>
                        </tr>
                    ))
                )}
            </tbody>
        </table>
      </div>
    </div>
  );
}