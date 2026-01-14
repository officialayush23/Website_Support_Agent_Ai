import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { toast } from 'sonner';
import { MessageSquare, CheckCircle, Loader2, Clock } from 'lucide-react';

export default function AdminSupport() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComplaints();
  }, []);

  const fetchComplaints = async () => {
    try {
      const data = await apiRequest('/admin/complaints/');
      setComplaints(data);
    } catch (err) {
      toast.error("Failed to load tickets");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (id, newStatus) => {
    try {
      await apiRequest(`/admin/complaints/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus })
      });
      
      setComplaints(prev => prev.map(c => c.id === id ? { ...c, status: newStatus } : c));
      toast.success(`Ticket marked as ${newStatus}`);
    } catch (err) {
      toast.error("Failed to update status");
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
        case 'open': return 'bg-red-100 text-red-700 border-red-200';
        case 'in_progress': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
        case 'resolved': return 'bg-green-100 text-green-700 border-green-200';
        default: return 'bg-gray-100 text-gray-700';
    }
  };

  if (loading) return <div className="flex justify-center p-10"><Loader2 className="animate-spin text-gray-400" /></div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Support Tickets</h1>
        <div className="text-sm text-gray-500">Manage customer complaints</div>
      </div>

      <div className="grid gap-4">
        {complaints.length === 0 ? (
            <div className="text-center py-10 text-gray-500 bg-white rounded-xl border border-dashed">
                No active complaints found.
            </div>
        ) : (
            complaints.map((ticket) => (
                <div key={ticket.id} className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm flex flex-col md:flex-row justify-between gap-4">
                    <div className="flex gap-4">
                        <div className="mt-1">
                            <div className="bg-blue-50 p-3 rounded-full text-blue-600">
                                <MessageSquare size={20} />
                            </div>
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-gray-900">Order #{ticket.order_id?.slice(0,8)}...</h3>
                                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(ticket.status)}`}>
                                    {ticket.status.replace('_', ' ').toUpperCase()}
                                </span>
                            </div>
                            <p className="text-gray-600">{ticket.description}</p>
                            <p className="text-xs text-gray-400 mt-2">{new Date(ticket.created_at).toLocaleString()}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {ticket.status !== 'resolved' && (
                            <>
                                <button 
                                    onClick={() => handleUpdateStatus(ticket.id, 'in_progress')}
                                    className="px-3 py-1.5 text-sm font-medium text-yellow-700 bg-yellow-50 hover:bg-yellow-100 rounded-lg border border-yellow-200 flex items-center gap-1"
                                >
                                    <Clock size={14} /> In Progress
                                </button>
                                <button 
                                    onClick={() => handleUpdateStatus(ticket.id, 'resolved')}
                                    className="px-3 py-1.5 text-sm font-medium text-green-700 bg-green-50 hover:bg-green-100 rounded-lg border border-green-200 flex items-center gap-1"
                                >
                                    <CheckCircle size={14} /> Resolve
                                </button>
                            </>
                        )}
                    </div>
                </div>
            ))
        )}
      </div>
    </div>
  );
}