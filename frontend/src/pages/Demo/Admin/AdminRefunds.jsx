import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { DollarSign, Check, X, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function AdminRefunds() {
  const [refunds, setRefunds] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadRefunds(); }, []);

  const loadRefunds = async () => {
    try {
      const data = await api.get('/refunds/admin');
      setRefunds(data);
    } catch (err) { toast.error("Fetch failed"); } 
    finally { setLoading(false); }
  };

  const updateStatus = async (id, status) => {
    try {
      await api.patch(`/refunds/${id}`, { status });
      toast.success(`Refund ${status}`);
      loadRefunds();
    } catch (err) { toast.error("Update failed"); }
  };

  return (
    <div className="space-y-6 animate-in fade-in">
       <h1 className="text-2xl font-bold">Refund Requests</h1>
       
       <div className="grid gap-4">
         {loading ? <Loader2 className="animate-spin text-gray-400 mx-auto"/> : refunds.map(r => (
           <div key={r.id} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="flex items-start gap-4">
                 <div className="bg-orange-100 p-3 rounded-full text-orange-600"><DollarSign size={24}/></div>
                 <div>
                    <h3 className="font-bold text-gray-900">Order #{r.order_id.slice(0,8)}</h3>
                    <p className="text-gray-600 text-sm mt-1">Reason: "{r.reason}"</p>
                    <p className="text-xs text-gray-400 mt-2">{new Date(r.created_at).toLocaleString()}</p>
                 </div>
              </div>

              <div className="flex items-center gap-3">
                 {r.status === 'initiated' ? (
                   <>
                     <button onClick={() => updateStatus(r.id, 'rejected')} className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700 text-sm">
                       <X size={16}/> Reject
                     </button>
                     <button onClick={() => updateStatus(r.id, 'approved')} className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                       <Check size={16}/> Approve
                     </button>
                   </>
                 ) : (
                   <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${r.status === 'approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                     {r.status}
                   </span>
                 )}
              </div>
           </div>
         ))}
         {!loading && refunds.length === 0 && <p className="text-center text-gray-500 py-10">No pending refunds.</p>}
       </div>
    </div>
  );
}