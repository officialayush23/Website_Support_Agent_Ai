import React, { useEffect, useRef, useState } from 'react'
import {
    ArrowUp,
    Plus,
    Bot,
    User,
    ShoppingCart,
    List,
    UserCircle,
    Package, // --- ADDED ---
    AlertTriangle, // --- ADDED ---
    CornerDownLeft // --- ADDED ---
} from "lucide-react"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "../ui/dropdown-menu"
import {
    InputGroup,
    InputGroupAddon,
    InputGroupButton,
    InputGroupTextarea, // Using this from your import
} from "@/components/ui/input-group"
import { Separator } from "@/components/ui/separator"
import ModeToggle from '../use_ui/ModeToggle'
import LogoutButton from '../auth/Logout'
// Note: I'm assuming all imports above are correct as per your project structure.

// =================================================================================
// --- NEW: UI Render Components ---
// These components will render the different JSON payloads from the bot.
// =================================================================================

/**
 * Renders a simple text message.
 */
const RenderTextMessage = ({ payload }) => (
    <p className="whitespace-pre-wrap">{payload}</p>
);

/**
 * Renders user profile data in a table.
 */
const RenderProfileData = ({ payload }) => (
    <div className="overflow-x-auto">
        <div className="flex items-center gap-2 text-lg font-semibold mb-2">
            <UserCircle className="w-5 h-5" />
            <span>Your Profile</span>
        </div>
        <table className="min-w-full divide-y divide-gray-500">
            <tbody className="divide-y divide-gray-600">
                {Object.entries(payload).map(([key, value]) => {
                    // Don't render internal keys like user_id or password_hash
                    if (key === 'user_id' || key === 'password_hash') return null;
                    return (
                        <tr key={key}>
                            <td className="px-4 py-2 text-sm font-medium capitalize whitespace-nowrap">{key.replace('_', ' ')}</td>
                            <td className="px-4 py-2 text-sm whitespace-nowrap">{String(value || 'N/A')}</td>
                        </tr>
                    )
                })}
            </tbody>
        </table>
    </div>
);
/**
 * Renders a list of products.
 */
const RenderProductList = ({ payload }) => {
    // --- FIX: Check if payload is an array ---
    if (!Array.isArray(payload) || payload.length === 0) {
        return <RenderTextMessage payload="No products found." />;
    }

    return (
        <div className="space-y-3">
            {payload.map((product, index) => (
                <div key={index} className="p-3 border border-gray-500 rounded-lg">
                    <p className="font-semibold">{product.name}</p>
                    {/* Added alt text and safety check for image */}
                    {product.image_url && <img src={product.image_url} alt={product.name} className="m-1 rounded-md" />}
                    <p className="text-sm">Price: ${product.price}</p>
                    <p className="text-sm">Description: {product.description}</p>
                    {product.stock && <p className="text-sm">Stock: {product.stock}</p>}
                </div>
            ))}
        </div>
    );
};

/**
 * Renders a list of cart items.
 */
const RenderCartItems = ({ payload }) => {
    // --- FIX: Check if payload is an array ---
    if (!Array.isArray(payload) || payload.length === 0) {
        return <RenderTextMessage payload="Your cart is empty." />;
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 text-lg font-semibold">
                <ShoppingCart className="w-5 h-5" />
                <span>Your Cart</span>
            </div>
            {payload.map((item, index) => (
                <div key={index} className="flex justify-between p-2 border border-gray-500 rounded-lg">
                    <span>{item.product_name}</span>
                    <span className="font-medium">Qty: {item.quantity}</span>
                </div>
            ))}
        </div>
    );
};

const RenderOrderList = ({ payload }) => {
    // --- FIX: Check if payload is an array ---
    if (!Array.isArray(payload) || payload.length === 0) {
        return <RenderTextMessage payload="You have no orders." />;
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 text-lg font-semibold">
                <Package className="w-5 h-5" />
                <span>Your Orders</span>
            </div>
            {payload.map((order, index) => (
                <div key={index} className="p-3 border border-gray-500 rounded-lg">
                    <p className="font-semibold">Order ID: {order.order_id}</p>
                    <p className="text-sm">Status: {order.status}</p>
                    <p className="text-sm">Total: ${order.total_amount}</p>
                    <p className="text-sm">Date: {new Date(order.order_date).toLocaleDateString()}</p>
                </div>
            ))}
        </div>
    );
};


const RenderComplaintList = ({ payload }) => {
    // --- FIX: Check if payload is an array ---
    if (!Array.isArray(payload) || payload.length === 0) {
        return <RenderTextMessage payload="You have no complaints." />;
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 text-lg font-semibold">
                <AlertTriangle className="w-5 h-5" />
                <span>Your Complaints</span>
            </div>
            {payload.map((complaint, index) => (
                <div key={index} className="p-3 border border-gray-500 rounded-lg">
                    <p className="font-semibold">Complaint ID: {complaint.complaint_id}</p>
                    <p className="text-sm">Order ID: {complaint.order_id || 'N/A'}</p>
                    <p className="text-sm">Status: {complaint.status}</p>
                    <p className="text-sm line-clamp-2">Description: {complaint.description}</p>
                </div>
            ))}
        </div>
    );
};

const RenderReturnList = ({ payload }) => {
    // --- FIX: Check if payload is an array ---
    if (!Array.isArray(payload) || payload.length === 0) {
        return <RenderTextMessage payload="You have no return requests." />;
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 text-lg font-semibold">
                <CornerDownLeft className="w-5 h-5" />
                <span>Your Returns</span>
            </div>
            {payload.map((ret, index) => (
                <div key={index} className="p-3 border border-gray-500 rounded-lg">
                    <p className="font-semibold">Return ID: {ret.return_id}</p>
                    <p className="text-sm">Order ID: {ret.order_id}</p>
                    <p className="text-sm">Product ID: {ret.product_id}</p>
                    <p className="text-sm">Status: {ret.status}</p>
                    <p className="text-sm line-clamp-2">Reason: {ret.reason}</p>
                </div>
            ))}
        </div>
    );
};


/**
 * Renders clickable action buttons.
 */
const RenderActionOptions = ({ payload, onOptionClick }) => {
    // --- FIX: Check if payload is an array ---
    if (!Array.isArray(payload) || payload.length === 0) {
        return null; // Don't render anything if there are no options
    }

    return (
        <div className="flex flex-wrap gap-2">
            {payload.map((option, index) => (
                <button
                    key={index}
                    onClick={() => onOptionClick(option)}
                    className="px-3 py-1.5 text-sm font-medium text-white bg-purple-600 rounded-full hover:bg-purple-700 transition-colors"
                >
                    {option}
                </button>
            ))}
        </div>
    );
};


// =================================================================================
// --- Main Chatbot Component ---
// =================================================================================

function Chatbot() {
    const [value, setValue] = useState("")
    const textareaRef = useRef(null)
    const MAX_HEIGHT = 200

    // --- MODIFIED: State for messages and loading ---
    // Messages are now objects with { sender, type, payload }
    const [messages, setMessages] = useState([
        { sender: 'bot', type: 'text', payload: "Hello! How can I assist you today?" }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null); // Ref for auto-scrolling
    // ------------------------------------------

    useEffect(() => {
        const textarea = textareaRef.current
        if (!textarea) return

        textarea.style.height = "auto"
        const newHeight = Math.min(textarea.scrollHeight, MAX_HEIGHT)
        textarea.style.height = `${newHeight}px`
        textarea.style.overflowY =
            textarea.scrollHeight > MAX_HEIGHT ? "auto" : "hidden"
    }, [value])

    // --- Auto-scroll to bottom ---
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);
    // ----------------------------------

    // --- sendToBot function (unchanged) ---
    const sendToBot = async (message) => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            console.error("No auth token found. Please log in.");
            return { type: "text", payload: "Error: Authentication required. Please log in again." };
        }

        const res = await fetch("http://127.0.0.1:8000/api/chatbot/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ message }),
        });
        // Handle non-JSON responses (like 500 errors)
        if (!res.ok) {
            const errorText = await res.text();
            console.error("Backend error:", errorText);
            return { type: "text", payload: `Sorry, an error occurred on the server (Code: ${res.status}).` };
        }
        const data = await res.json();
        return data; // Return the full data { type, payload }
    };
    // ------------------------------------

    // --- REFACTORED: Handle message submission ---
    /**
     * Universal function to send a message to the bot and get a response.
     */
    const sendMessage = async (messageText) => {
        if (!messageText || isLoading) return; // Prevent sending empty or during load

        // 1. Add user message to state
        const userMessage = { sender: 'user', type: 'text', payload: messageText };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        try {
            // 2. Send message to bot and get JSON response
            const data = await sendToBot(messageText);

            // 3. Add bot response to state
            // The 'data' is already in the { type, payload } format
            const botMessage = { sender: 'bot', type: data.type, payload: data.payload };
            setMessages(prev => [...prev, botMessage]);

        } catch (error) {
            console.error("Failed to send message:", error);
            const errorMessage = { sender: 'bot', type: 'text', payload: "Sorry, I'm having trouble connecting. Please try again." };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Handles the form <textarea> submission.
     */
    const handleFormSubmit = () => {
        const messageText = value.trim();
        if (messageText) {
            sendMessage(messageText);
            setValue(""); // Clear input
        }
    };

    /**
     * Handles a click on a quick-reply button.
     */
    const handleOptionClick = (optionText) => {
        sendMessage(optionText); // Send the button's text as a new message
    };

    // --- Handle 'Enter' key press ---
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleFormSubmit();
        }
    };
    // ----------------------------------

    /**
     * Main component to switch between different message renderers.
     */
    const RenderMessage = ({ msg }) => {
        let content;
        // --- FIX: Add safety check for msg.payload ---
        const payload = msg.payload ?? "No content"; // Default payload to prevent crashes

        switch (msg.type) {
            case 'text':
                content = <RenderTextMessage payload={payload} />;
                break;
            case 'profile_data':
                content = <RenderProfileData payload={payload} />;
                break;
            case 'product_list':
                content = <RenderProductList payload={payload} />;
                break;
            case 'cart_items':
                content = <RenderCartItems payload={payload} />;
                break;
            // --- NEW: Added cases for new renderers ---
            case 'order_list':
                content = <RenderOrderList payload={payload} />;
                break;
            case 'complaint_list':
                content = <RenderComplaintList payload={payload} />;
                break;
            case 'return_list':
                content = <RenderReturnList payload={payload} />;
                break;
            case 'action_options':
                content = <RenderActionOptions payload={payload} onOptionClick={handleOptionClick} />;
                break;
            default:
                console.warn("Unknown message type:", msg.type);
                content = <RenderTextMessage payload="Error: I received a message I don't understand." />;
        }

        const isUser = msg.sender === 'user';

        return (
            <div
                className={`flex items-start gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
                {!isUser && (
                    <div className="p-2 bg-purple-700 rounded-full">
                        <Bot className="w-5 h-5" />
                    </div>
                )}

                <div
                    className={`max-w-xs md:max-w-md lg:max-w-lg p-3 rounded-2xl ${isUser
                        ? 'dark:bg-primary bg-cyan-400 text-primary-foreground rounded-br-none'
                        : 'dark:bg-black bg-purple-700 text-white rounded-bl-none'
                        }`}
                > {/* --- FIX: Removed stray 'T' prop --- */}
                    {content}
                </div>

                {isUser && (
                    <div className="p-2 bg-cyan-600 rounded-full">
                        <User className="w-5 h-5" />
                    </div>
                )}
            </div>
        );
    };


    return (
        <section className="relative h-full w-full transition-all duration-300 flex flex-col">
            <div className="flex justify-between items-center px-4 py-2">
                <LogoutButton className="cursor-pointer" />
                <ModeToggle className="cursor-pointer" />
            </div>

            {/* --- MODIFIED: Chat messages area --- */}
            <div className="flex-1 transition-all dark:bg-neutral-800 bg-gray-100 rounded-2xl duration-300 overflow-y-auto p-4 m-2 space-y-4">

                {messages.map((msg, index) => (
                    // Use the new RenderMessage component
                    <RenderMessage key={index} msg={msg} />
                ))}

                {/* Show "Bot is typing..." */}
                {isLoading && (
                    <div className="flex items-start gap-3 justify-start">
                        <div className="p-2 bg-muted rounded-full">
                            <Bot className="w-5 h-5" />
                        </div>
                        <div className="p-3 rounded-2xl bg-muted text-muted-foreground rounded-bl-none">
                            <p className="italic">Daksha.ai is typing...</p>
                        </div>
                    </div>
                )}

                {/* Empty div for auto-scrolling */}
                <div ref={messagesEndRef} />
            </div>
            {/* ---------------------------------- */}


            {/* Fixed input section */}
            <div className="sticky relative  transition-all duration-300 bottom-0 w-full border-t  border-gray-700 p-2">
                <div className="absolute inset-0 rounded-xl border-[2px] border-transparent bg-[conic-gradient(from_0deg,theme(colors.pink.500),theme(colors.purple.500),theme(colors.blue.500),theme(colors.pink.500))] bg-[length:200%_200%] animate-gradient-spin"></div>
                <InputGroup className='rounded-3xl'>
                    <InputGroupTextarea placeholder="Ask, Search or Chat..."
                        ref={textareaRef}
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        onKeyDown={handleKeyDown} // --- WIRED UP ---
                        className="resize-none transition-all duration-3One00  p-3 focus-visible:ring-0 focus-visible:outline-none min-h-[52px]"
                    />
                    <InputGroupAddon align="inline-end">
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <InputGroupButton
                                    variant="outline"
                                    className="rounded-full"
                                    size="icon-md"
                                >
                                    <Plus />
                                </InputGroupButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                side="top"
                                align="center"
                                className="[--radius:0.95rem] transition-all duration-300"
                            >
                                <DropdownMenuItem>Auto</DropdownMenuItem>
                                <DropdownMenuItem>Agent</DropdownMenuItem>
                                <DropdownMenuItem>Manual</DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>

                        <Separator orientation="vertical" className="!h-4" />

                        <InputGroupButton
                            variant="default"
                            className="rounded-full ml-auto transition-all duration-300"
                            size="icon-md"
                            onClick={handleFormSubmit} // --- MODIFIED ---
                            disabled={isLoading} // --- WIRED UP ---
                        >
                            <ArrowUp />
                            <span className="sr-only">Send</span>
                        </InputGroupButton>
                    </InputGroupAddon>
                </InputGroup>
            </div>
        </section>
    )
}

export default Chatbot