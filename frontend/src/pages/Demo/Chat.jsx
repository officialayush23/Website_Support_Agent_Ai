import React, { useState, useEffect, useRef } from 'react';
import { api, analytics } from '../../lib/api';
import { useAuth } from '../../context/AuthContext';
import { Send, Bot, User, Loader2, ShoppingBag, Sparkles, ArrowRight, X } from 'lucide-react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';

export default function ChatInterface() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const scrollRef = useRef(null);

  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  // Initialize Chat
  useEffect(() => {
    initSession();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const initSession = async () => {
    try {
      // Create new session
      const res = await api.post('/chat/chat-sessions');
      setSessionId(res.chat_session_id);
      
      // If navigated with context (e.g. from Order Detail), send it automatically
      if (location.state?.context) {
        handleSendMessage(location.state.context);
      } else {
        // Initial greeting
        setMessages([{
          role: 'assistant',
          content: `Hi ${user?.user_metadata?.full_name?.split(' ')[0] || 'there'}! I'm your AI fashion assistant. Looking for an outfit or checking an order?`,
          created_at: new Date().toISOString()
        }]);
      }
    } catch (err) {
      toast.error("Failed to start chat session");
    }
  };

  const handleSendMessage = async (text = input) => {
    if (!text.trim() || !sessionId) return;

    const userMsg = { role: 'user', content: text, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setIsTyping(true);

    try {
      const res = await api.post(`/chat/sessions/${sessionId}/messages`, { content: text });
      
      // Artificial delay for "typing" feel if response is too fast
      await new Promise(r => setTimeout(r, 600));

      const aiMsg = {
        role: 'assistant',
        content: res.message,
        products: res.actions?.filter(a => a.type === 'recommend_product') || [], // Assuming backend structure
        handoff: res.handoff,
        created_at: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMsg]);
      analytics.track('chat_message', { metadata: { length: text.length } });

      if (res.handoff) {
        toast("Connecting you to a human agent...", { icon: '🎧' });
      }

    } catch (err) {
      toast.error("Failed to send message");
    } finally {
      setLoading(false);
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] max-w-4xl mx-auto bg-white rounded-2xl border border-gray-200 shadow-xl overflow-hidden mt-4">
      {/* Header */}
      <div className="bg-gray-900 p-4 flex items-center justify-between text-white">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-blue-400 to-purple-500 p-2 rounded-full">
            <Bot size={24} className="text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg">AI Stylist</h1>
            <p className="text-xs text-gray-400 flex items-center gap-1">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> Online
            </p>
          </div>
        </div>
        <button onClick={() => navigate('/demo')} className="p-2 hover:bg-white/10 rounded-full"><X size={20}/></button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50/50" ref={scrollRef}>
        {messages.map((msg, idx) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            key={idx} 
            className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-gray-200' : 'bg-gray-900 text-white'}`}>
              {msg.role === 'user' ? <User size={20} /> : <Sparkles size={18} />}
            </div>

            {/* Bubble */}
            <div className={`max-w-[80%] space-y-2`}>
              <div className={`p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-br-none' 
                  : 'bg-white border border-gray-100 text-gray-700 rounded-bl-none'
              }`}>
                {msg.content}
              </div>

              {/* Render Recommended Products inside Chat */}
              {msg.products && msg.products.length > 0 && (
                <div className="flex gap-4 overflow-x-auto py-2 no-scrollbar">
                  {msg.products.map((item, i) => (
                    <div key={i} className="min-w-[200px] bg-white rounded-xl border border-gray-200 overflow-hidden shadow-md group">
                      <div className="h-32 bg-gray-100 relative">
                        {/* Placeholder image logic needed here based on backend response */}
                         <div className="absolute inset-0 flex items-center justify-center text-gray-300"><ShoppingBag/></div>
                      </div>
                      <div className="p-3">
                        <p className="font-bold text-gray-900 text-sm truncate">{item.payload?.product_name || "Product"}</p>
                        <p className="text-blue-600 font-medium text-xs mt-1">${item.payload?.price || "0.00"}</p>
                        <button 
                          onClick={() => navigate('/demo')} 
                          className="mt-2 w-full bg-gray-900 text-white text-xs py-1.5 rounded flex items-center justify-center gap-1 hover:bg-black"
                        >
                          View Details <ArrowRight size={10}/>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        ))}

        {isTyping && (
          <div className="flex gap-4">
             <div className="w-10 h-10 rounded-full bg-gray-900 flex items-center justify-center"><Sparkles size={18} className="text-white"/></div>
             <div className="bg-white border border-gray-100 p-4 rounded-2xl rounded-bl-none shadow-sm flex items-center gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></span>
             </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-100">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
          className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-full px-2 py-2 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all"
        >
          <input
            className="flex-1 bg-transparent px-4 py-2 focus:outline-none text-sm text-gray-700"
            placeholder="Ask about clothes, orders, or style..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button 
            type="submit" 
            disabled={!input.trim() || loading}
            className="p-3 bg-gray-900 text-white rounded-full hover:bg-blue-600 disabled:opacity-50 disabled:bg-gray-300 transition-colors shadow-lg"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </form>
      </div>
    </div>
  );
}