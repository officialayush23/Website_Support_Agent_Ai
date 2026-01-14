import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { toast } from 'sonner';
import { User, MessageSquare, ArrowRight, Loader2 } from 'lucide-react';

export default function AdminHandoff() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHandoffs();
  }, []);

  const fetchHandoffs = async () => {
    try {
      // Calls the new GET /support/admin/conversations/ai-handoffs endpoint
      // Note: You might need to adjust query params based on what you want to see (e.g. ?unassigned=true)
      const data = await apiRequest('/support/admin/conversations/ai-handoffs?unassigned=true');
      setConversations(data);
    } catch (err) {
      toast.error("Failed to load handoffs");
    } finally {
      setLoading(false);
    }
  };

  const handleTakeover = (convId) => {
      // In a real app, this would assign the conversation to the agent
      // and redirect to a chat view. For now, we'll just log/toast.
      toast.success(`Joined conversation ${convId}`);
      console.log(`Maps to /admin/chat/${convId}`);
  };

  if (loading) return <div className="flex justify-center p-10"><Loader2 className="animate-spin text-gray-400" /></div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Handoffs</h1>
            <p className="text-sm text-gray-500">Conversations requiring human attention.</p>
        </div>
      </div>

      <div className="grid gap-4">
        {conversations.length === 0 ? (
            <div className="text-center py-10 text-gray-500 bg-white rounded-xl border border-dashed">
                <span className="block text-2xl mb-2">🎉</span>
                No active handoffs. The AI is handling everything!
            </div>
        ) : (
            conversations.map((conv) => (
                <div key={conv.id} className="bg-white p-5 rounded-xl border border-red-100 shadow-sm flex items-center justify-between group hover:border-red-200 transition-all">
                    <div className="flex items-center gap-4">
                        <div className="bg-red-50 p-3 rounded-full text-red-600">
                            <User size={24} />
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-900">User {conv.user_id?.slice(0,8)}...</h3>
                            <p className="text-xs text-gray-500">Started: {new Date(conv.created_at).toLocaleString()}</p>
                            <span className="inline-flex mt-1 items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                {conv.status || 'Needs Attention'}
                            </span>
                        </div>
                    </div>
                    
                    <button 
                        onClick={() => handleTakeover(conv.id)}
                        className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-black transition-colors flex items-center gap-2 shadow-md"
                    >
                        Take Over <ArrowRight size={16} />
                    </button>
                </div>
            ))
        )}
      </div>
    </div>
  );
}