import React, { useEffect, useState, useRef } from 'react';
import { apiRequest } from '../../../lib/api';
import { useAuth } from '../../../context/AuthContext';
import { Send, User, Bot, AlertCircle, CheckCircle, Hand } from 'lucide-react';
import { toast } from 'sonner';

export default function AdminSupport() {
    const [conversations, setConversations] = useState([]);
    const [activeConvo, setActiveConvo] = useState(null);
    const [messages, setMessages] = useState([]);
    const [reply, setReply] = useState('');
    const { user } = useAuth();
    const messagesEndRef = useRef(null);

    // Poll Queue
    useEffect(() => {
        const fetchQueue = async () => {
            const data = await apiRequest('/support/admin/conversations/ai-handoffs?status=active');
            setConversations(data);
        };
        fetchQueue();
        const interval = setInterval(fetchQueue, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    // Load Messages
    useEffect(() => {
        if (activeConvo) {
            apiRequest(`/support/conversations/${activeConvo.id}/messages`).then(setMessages);
        }
    }, [activeConvo]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleJoin = async () => {
        try {
            await apiRequest(`/support/conversations/${activeConvo.id}/join`, { method: 'POST' });
            toast.success("Joined conversation");
            setActiveConvo({ ...activeConvo, assigned_to: user.id });
        } catch (e) {
            toast.error("Failed to join");
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!reply.trim()) return;

        try {
            await apiRequest(`/support/conversations/${activeConvo.id}/messages`, {
                method: 'POST',
                body: JSON.stringify({ content: reply })
            });
            setMessages([...messages, { role: 'assistant', content: reply, created_at: new Date().toISOString() }]);
            setReply('');
        } catch (err) {
            toast.error("Failed to send");
        }
    };

    return (
        <div className="h-[calc(100vh-140px)] flex gap-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            {/* Sidebar List */}
            <div className="w-80 border-r border-gray-200 dark:border-gray-700 flex flex-col">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                    <h2 className="font-bold dark:text-white flex items-center gap-2">
                        <AlertCircle className="text-orange-500" size={18} />
                        Handoff Queue ({conversations.length})
                    </h2>
                </div>
                <div className="flex-1 overflow-y-auto">
                    {conversations.map(c => (
                        <div 
                            key={c.id}
                            onClick={() => setActiveConvo(c)}
                            className={`p-4 border-b border-gray-100 dark:border-gray-800 cursor-pointer hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors ${activeConvo?.id === c.id ? 'bg-blue-50 dark:bg-gray-700' : ''}`}
                        >
                            <div className="flex justify-between mb-1">
                                <span className="font-semibold text-sm dark:text-gray-200">User {c.user_id.substring(0,4)}</span>
                                <span className="text-xs text-gray-500">{new Date(c.handed_off_at).toLocaleTimeString()}</span>
                            </div>
                            <p className="text-xs text-red-500 font-medium truncate">{c.handoff_reason}</p>
                            {c.assigned_to ? (
                                <span className="text-[10px] bg-green-100 text-green-700 px-1 rounded mt-1 inline-block">Assigned</span>
                            ) : (
                                <span className="text-[10px] bg-red-100 text-red-700 px-1 rounded mt-1 inline-block">Unassigned</span>
                            )}
                        </div>
                    ))}
                    {conversations.length === 0 && (
                        <div className="p-8 text-center text-gray-400 text-sm">No active tickets</div>
                    )}
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col">
                {activeConvo ? (
                    <>
                        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-white dark:bg-gray-800">
                            <div>
                                <h3 className="font-bold dark:text-white">Support Chat</h3>
                                <p className="text-xs text-gray-500">ID: {activeConvo.id}</p>
                            </div>
                            
                            {!activeConvo.assigned_to ? (
                                <button onClick={handleJoin} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-sm">
                                    <Hand size={16} /> Join Conversation
                                </button>
                            ) : (
                                <div className="text-green-600 text-sm font-medium flex items-center gap-2 bg-green-50 px-3 py-1 rounded-full">
                                    <CheckCircle size={16} /> You joined this chat
                                </div>
                            )}
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
                            {messages.map((m, i) => (
                                <div key={i} className={`flex ${m.role === 'user' ? 'justify-start' : 'justify-end'}`}>
                                    <div className={`max-w-[70%] rounded-2xl px-4 py-3 shadow-sm ${
                                        m.role === 'user' 
                                            ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700' 
                                            : 'bg-blue-600 text-white'
                                    }`}>
                                        <p className="text-sm">{m.content}</p>
                                        <span className="text-[10px] opacity-70 mt-1 block">
                                            {m.role === 'user' ? 'Customer' : 'Agent'} • {new Date(m.created_at).toLocaleTimeString()}
                                        </span>
                                    </div>
                                </div>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>

                        <form onSubmit={handleSend} className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex gap-2">
                            <input 
                                className="flex-1 bg-gray-100 dark:bg-gray-900 border-0 rounded-lg px-4 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder={activeConvo.assigned_to ? "Type a reply..." : "Join conversation to reply"}
                                value={reply}
                                onChange={e => setReply(e.target.value)}
                                disabled={!activeConvo.assigned_to}
                            />
                            <button type="submit" disabled={!activeConvo.assigned_to} className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
                                <Send size={20} />
                            </button>
                        </form>
                    </>
                ) : (
                    <div className="flex-1 flex items-center justify-center text-gray-400 flex-col gap-4">
                        <Bot size={48} className="opacity-20" />
                        <p>Select a conversation from the queue</p>
                    </div>
                )}
            </div>
        </div>
    );
}