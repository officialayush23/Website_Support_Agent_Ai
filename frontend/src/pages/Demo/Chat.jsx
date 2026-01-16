import React, { useEffect, useState, useRef } from 'react';
import { apiRequest } from '../../lib/api';
import { useAuth } from '../../context/AuthContext';
import { useLocation } from 'react-router-dom';
import { 
  Send, Mic, MicOff, Volume2, VolumeX, Bot, Loader2, ShoppingBag 
} from 'lucide-react';
import { toast } from 'sonner';

export default function ChatInterface() {
  const { session } = useAuth();
  const location = useLocation();
  
  // State
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false); // Used for "Thinking..." state
  const [conversationId, setConversationId] = useState(null);
  const [isInitializing, setIsInitializing] = useState(true);
  
  // Voice State
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef(null);
  const scrollRef = useRef(null);

  // 1. Initialize Conversation & Load History
  useEffect(() => {
    const initChat = async () => {
      if (!session?.access_token) return;

      try {
        setIsInitializing(true);
        
        // A. Start/Resume Conversation
        const convoRes = await apiRequest('/support/conversations', { method: 'POST' });
        const id = convoRes.conversation_id;
        setConversationId(id);

        // B. Load History
        const historyRes = await apiRequest(`/support/conversations/${id}/messages`);
        
        // Map DB history to UI format
        // Note: Historical messages might not have 'products' unless stored in metadata. 
        // We default to empty array for history.
        const formattedHistory = historyRes.map(msg => ({
            role: msg.role,
            content: msg.content,
            products: [] 
        }));

        setMessages(formattedHistory);

        // C. Handle Context (Hidden System Prompt)
        // If navigated from Order page, send context silently
        if (location.state?.context) {
            await sendHiddenContext(id, location.state.context);
            // Clear state to prevent loop
            window.history.replaceState({}, document.title);
        }

      } catch (err) {
        console.error("Chat Init Error:", err);
        toast.error("Failed to connect to support assistant.");
      } finally {
        setIsInitializing(false);
      }
    };

    initChat();
  }, [session, location.state]);

  // Helper to send hidden context
  const sendHiddenContext = async (id, contextText) => {
      try {
          await apiRequest(`/support/conversations/${id}/messages`, {
              method: 'POST',
              body: JSON.stringify({ content: `[System Context: ${contextText}]` })
          });
      } catch (e) {
          console.error("Context send failed", e);
      }
  };

  // 2. Send Message (REST API)
  const sendMessage = async (e) => {
    e?.preventDefault();
    
    if (!input.trim() || !conversationId || isTyping) return;

    const userText = input;
    setInput('');
    setIsTyping(true);

    // Optimistic UI Update
    setMessages(prev => [...prev, { role: 'user', content: userText, products: [] }]);

    try {
        // Call Backend API
        const response = await apiRequest(`/support/conversations/${conversationId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ content: userText })
        });

        // Backend returns the AI response immediately
        const aiMessage = {
            role: 'assistant',
            content: response.content,
            products: response.products || []
        };

        setMessages(prev => [...prev, aiMessage]);
        
        // Trigger Voice Output
        speak(response.content);

    } catch (err) {
        console.error("Send Error:", err);
        toast.error("Failed to send message. Please try again.");
        // Optional: Remove the optimistic message on failure
    } finally {
        setIsTyping(false);
    }
  };

  // --- Voice Input Logic (Web Speech API) ---
  const toggleListening = () => {
      if (isListening) {
          recognitionRef.current?.stop();
          setIsListening(false);
      } else {
          if (!('webkitSpeechRecognition' in window)) {
              toast.error("Voice input not supported in this browser.");
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
          };
          
          recognitionRef.current = recognition;
          recognition.start();
      }
  };

  // --- Voice Output Logic (SpeechSynthesis) ---
  const speak = (text) => {
      if (!text) return;
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
  };

  // Auto-scroll
  useEffect(() => {
      scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="p-4 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 text-blue-600 rounded-lg"><Bot size={20} /></div>
                <div>
                    <h3 className="font-bold text-gray-900">Weeb Assistant</h3>
                    <div className="flex items-center gap-2">
                        <span className={`h-2 w-2 rounded-full ${conversationId ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'}`}></span>
                        <p className="text-xs text-gray-500">{conversationId ? 'Online' : 'Initializing...'}</p>
                    </div>
                </div>
            </div>
            <div className="flex gap-2">
                <button onClick={() => window.speechSynthesis.cancel()} className={`p-2 rounded-full hover:bg-gray-200 transition-colors ${isSpeaking ? 'text-blue-600' : 'text-gray-400'}`}>
                    {isSpeaking ? <Volume2 size={18} className="animate-pulse" /> : <VolumeX size={18} />}
                </button>
            </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-50/30">
            {messages.length === 0 && !isInitializing && (
                <div className="text-center py-10 text-gray-400 text-sm">
                    <Bot className="mx-auto h-8 w-8 mb-2 opacity-50" />
                    Start a conversation with Weeb AI...
                </div>
            )}

            {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] rounded-2xl p-4 shadow-sm ${
                        msg.role === 'user' 
                            ? 'bg-blue-600 text-white rounded-tr-none' 
                            : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none'
                    }`}>
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                        
                        {/* Horizontal Product Recommendation Grid */}
                        {msg.products && msg.products.length > 0 && (
                            <div className="mt-4 pt-3 border-t border-gray-100/20">
                                <p className="text-[10px] uppercase font-bold mb-2 opacity-80 flex items-center gap-1">
                                    <ShoppingBag size={10} /> Recommended
                                </p>
                                <div className="flex gap-3 overflow-x-auto pb-2 no-scrollbar">
                                    {msg.products.map(prod => (
                                        <div 
                                            key={prod.id} 
                                            className="min-w-[130px] w-[130px] md:min-w-[160px] md:w-[160px] bg-white rounded-lg p-2 border border-gray-200 shadow-sm text-gray-900 flex-shrink-0 transition-transform hover:scale-105 cursor-pointer"
                                            onClick={() => window.open(`/demo/products/${prod.id}`, '_blank')}
                                        >
                                            <div className="h-24 md:h-32 bg-gray-100 rounded-md mb-2 overflow-hidden relative">
                                                <img 
                                                    src={prod.image || "https://ui.shadcn.com/placeholder.svg"} 
                                                    className="w-full h-full object-cover" 
                                                    alt={prod.name} 
                                                />
                                            </div>
                                            <p className="text-xs font-bold truncate">{prod.name}</p>
                                            <p className="text-xs text-green-600 font-medium">${prod.price}</p>
                                            <button className="mt-2 w-full bg-blue-50 text-blue-600 text-[10px] py-1.5 rounded font-bold hover:bg-blue-100 transition-colors">
                                                View
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            ))}
            
            {/* Typing Indicator */}
            {(isTyping || isInitializing) && (
                <div className="flex justify-start animate-in fade-in zoom-in-95 duration-300">
                    <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none p-3 shadow-sm flex items-center gap-2">
                        <Loader2 size={14} className="animate-spin text-blue-600" />
                        <span className="text-xs text-gray-400">
                            {isInitializing ? "Initializing..." : "Thinking..."}
                        </span>
                    </div>
                </div>
            )}
            <div ref={scrollRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-gray-100">
            <form onSubmit={sendMessage} className="flex items-center gap-2 bg-gray-50 p-2 rounded-xl border border-gray-200 focus-within:border-blue-300 focus-within:ring-4 focus-within:ring-blue-50 transition-all">
                <button 
                    type="button" 
                    onClick={toggleListening}
                    className={`p-3 rounded-lg transition-colors ${isListening ? 'bg-red-100 text-red-600 animate-pulse' : 'hover:bg-gray-200 text-gray-500'}`}
                    title="Voice Input"
                >
                    {isListening ? <MicOff size={20} /> : <Mic size={20} />}
                </button>
                
                <input 
                    className="flex-1 bg-transparent border-none focus:ring-0 text-sm outline-none px-2"
                    placeholder={isListening ? "Listening..." : "Type a message..."}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={isTyping || isInitializing}
                />
                
                <button 
                    type="submit" 
                    disabled={!input.trim() || isTyping || isInitializing}
                    className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-transform active:scale-95"
                >
                    <Send size={18} />
                </button>
            </form>
        </div>
    </div>
  );
}