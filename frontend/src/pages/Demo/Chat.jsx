import React, { useEffect, useState, useRef } from 'react';
import { apiRequest } from '../../lib/api';
import { useAuth } from '../../context/AuthContext';
import { useLocation } from 'react-router-dom';
import { 
  Send, Mic, MicOff, Volume2, VolumeX, Bot, User, Loader2, ShoppingBag 
} from 'lucide-react';

export default function ChatInterface() {
  const { user } = useAuth();
  const location = useLocation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  
  // Voice State
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef(null);
  const scrollRef = useRef(null);

  // Initialize
  useEffect(() => {
    startConversation();
  }, []);

  // Handle Incoming Context (e.g. from Order History)
  useEffect(() => {
    if (location.state?.context && conversationId) {
        sendMessage(`[Context: ${location.state.context}] I need help with this.`);
        // Clear state to avoid re-sending on refresh
        window.history.replaceState({}, document.title);
    }
  }, [conversationId, location.state]);

  const startConversation = async () => {
      try {
          const res = await apiRequest('/support/conversations', { method: 'POST' });
          setConversationId(res.conversation_id);
          setMessages([{ role: 'assistant', content: "Hello! I'm your AI support assistant. How can I help you today?" }]);
      } catch (err) {
          console.error("Chat init failed", err);
      }
  };

  const sendMessage = async (text = input) => {
    if (!text.trim() || !conversationId) return;

    const newMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, newMsg]);
    setInput('');
    setLoading(true);

    try {
        const res = await apiRequest(`/support/conversations/${conversationId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ content: text })
        });
        
        // Simulate/Fetch AI response (The backend should ideally return the AI reply in the response or we poll)
        // Assuming your backend processes synchronously or returns it:
        // If not, you might need to fetch the conversation history again. 
        // For this demo, let's assume we fetch the latest message or the backend returns it.
        // If your current API just returns "status: sent", we need to Poll or use WebSocket.
        // I'll simulate a fetch update here.
        
        // TODO: Implement Polling or WebSocket for real-time AI reply.
        // For demonstration, let's simulate a "Thinking..." delay then fetch history.
        setTimeout(async () => {
             // Mocking an AI response fetch since we don't have a direct "get latest message" endpoint in the provided routers
             // We would normally call GET /support/conversations/{id} here.
             
             // MOCK RESPONSE for Demo purposes if backend isn't returning AI text directly:
             const mockReply = { 
                 role: 'assistant', 
                 content: "I've received your request. Our team is looking into it.",
                 // Example of JSON product recommendation payload the AI might send
                 products: text.toLowerCase().includes('recommend') ? [
                     { id: '1', name: 'Summer Dress', price: 49.99, image: 'https://ui.shadcn.com/placeholder.svg' },
                     { id: '2', name: 'Beach Hat', price: 19.99, image: 'https://ui.shadcn.com/placeholder.svg' }
                 ] : null
             };
             
             setMessages(prev => [...prev, mockReply]);
             speak(mockReply.content);
             setLoading(false);
        }, 1500);

    } catch (err) {
        console.error("Message failed", err);
        setLoading(false);
    }
  };

  // --- Voice Input ---
  const toggleListening = () => {
      if (isListening) {
          recognitionRef.current?.stop();
          setIsListening(false);
      } else {
          if (!('webkitSpeechRecognition' in window)) {
              alert("Voice input not supported in this browser.");
              return;
          }
          const recognition = new window.webkitSpeechRecognition();
          recognition.continuous = false;
          recognition.interimResults = false;
          recognition.lang = 'en-US';
          
          recognition.onstart = () => setIsListening(true);
          recognition.onend = () => setIsListening(false);
          recognition.onresult = (event) => {
              const transcript = event.results[0][0].transcript;
              setInput(transcript);
              // Optional: Auto-send
              // sendMessage(transcript); 
          };
          
          recognitionRef.current = recognition;
          recognition.start();
      }
  };

  // --- Voice Output ---
  const speak = (text) => {
      if (!text) return;
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
      scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        
        {/* Chat Header */}
        <div className="p-4 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 text-blue-600 rounded-lg"><Bot size={20} /></div>
                <div>
                    <h3 className="font-bold text-gray-900">Weeb Assistant</h3>
                    <p className="text-xs text-gray-500">Always here to help</p>
                </div>
            </div>
            <div className="flex gap-2">
                <button onClick={() => window.speechSynthesis.cancel()} className="p-2 text-gray-400 hover:text-red-500">
                    {isSpeaking ? <Volume2 className="animate-pulse" /> : <VolumeX />}
                </button>
            </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-50/50">
            {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
                        msg.role === 'user' 
                            ? 'bg-blue-600 text-white rounded-tr-none' 
                            : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none'
                    }`}>
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                        
                        {/* Product Recommendations Grid (If JSON present) */}
                        {msg.products && (
                            <div className="mt-4 flex gap-3 overflow-x-auto pb-2 no-scrollbar">
                                {msg.products.map(prod => (
                                    <div key={prod.id} className="min-w-[140px] bg-white rounded-lg p-2 border border-gray-200 shadow-sm">
                                        <div className="h-24 bg-gray-100 rounded-md mb-2 overflow-hidden">
                                            <img src={prod.image} className="w-full h-full object-cover" alt="" />
                                        </div>
                                        <p className="text-xs font-bold text-gray-900 truncate">{prod.name}</p>
                                        <p className="text-xs text-gray-500">${prod.price}</p>
                                        <button className="mt-2 w-full bg-blue-50 text-blue-600 text-[10px] py-1 rounded font-bold hover:bg-blue-100">
                                            View
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            ))}
            {loading && (
                <div className="flex justify-start">
                    <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none p-4 shadow-sm flex items-center gap-2">
                        <Loader2 size={16} className="animate-spin text-blue-600" />
                        <span className="text-xs text-gray-400">Thinking...</span>
                    </div>
                </div>
            )}
            <div ref={scrollRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-gray-100">
            <form 
                onSubmit={(e) => { e.preventDefault(); sendMessage(); }}
                className="flex items-center gap-2 bg-gray-50 p-2 rounded-xl border border-gray-200 focus-within:border-blue-300 focus-within:ring-4 focus-within:ring-blue-50 transition-all"
            >
                <button 
                    type="button" 
                    onClick={toggleListening}
                    className={`p-3 rounded-lg transition-colors ${isListening ? 'bg-red-100 text-red-600 animate-pulse' : 'hover:bg-gray-200 text-gray-500'}`}
                >
                    {isListening ? <MicOff size={20} /> : <Mic size={20} />}
                </button>
                
                <input 
                    className="flex-1 bg-transparent border-none focus:ring-0 text-sm"
                    placeholder="Type or speak your message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                
                <button 
                    type="submit" 
                    disabled={!input.trim() || loading}
                    className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-transform active:scale-95"
                >
                    <Send size={18} />
                </button>
            </form>
        </div>
    </div>
  );
}