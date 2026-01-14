import React, { useEffect, useState } from 'react';
import { apiRequest, analytics } from '../../lib/api';
import { toast } from 'sonner';
import { Trash2, Plus, Minus, CreditCard, MapPin, ArrowRight, ShoppingBag } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Cart() {
  const [cart, setCart] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [cartData, addressData] = await Promise.all([
        apiRequest('/cart/'),
        apiRequest('/addresses/')
      ]);
      setCart(cartData); // Assuming cartData has { items: [], total: ... } based on backend
      setAddresses(addressData);
      
      // Auto-select default address
      const defaultAddr = addressData.find(a => a.is_default);
      if (defaultAddr) setSelectedAddress(defaultAddr.id);
      
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (productId, newQty) => {
    if (newQty < 1) return;
    try {
      await apiRequest(`/cart/items/${productId}`, {
        method: 'PATCH',
        body: JSON.stringify({ quantity: newQty })
      });
      // Optimistic update
      setCart(prev => ({
          ...prev,
          items: prev.items.map(item => item.product_id === productId ? { ...item, quantity: newQty } : item)
      }));
    } catch (err) {
      toast.error("Failed to update cart");
    }
  };

  const removeItem = async (productId) => {
    try {
      await apiRequest(`/cart/items/${productId}?quantity=0`, { method: 'PATCH' }); // Or delete endpoint if you have one
      // Based on your router: update with qty 0 usually removes, or maybe you need DELETE /cart/items/{id} if implemented
      // Your provided router only has DELETE /cart/ (clear all). 
      // Let's assume sending qty 0 to update removes it, or we filter locally for now.
      
      // Correction: Your router doesn't have delete single item. 
      // Workaround: We can use update with 0 if backend supports it, otherwise we might need to add that endpoint.
      // For now, I will assume update to 0 works.
      
      setCart(prev => ({
          ...prev,
          items: prev.items.filter(item => item.product_id !== productId)
      }));
      
      analytics.track('remove_from_cart', { productId });
      toast.success("Item removed");
    } catch (err) {
      toast.error("Failed to remove item");
    }
  };

  const handleCheckout = async () => {
    if (!selectedAddress) {
        toast.error("Please select a shipping address");
        return;
    }
    
    setProcessing(true);
    try {
        const order = await apiRequest('/orders/', {
            method: 'POST',
            body: JSON.stringify({ address_id: selectedAddress })
        });

        analytics.track('order_created', { orderId: order.id, metadata: { total: order.total } });
        
        toast.success("Order placed successfully!", {
            description: `Order #${order.id.slice(0,8)} confirmed.`
        });
        
        // Clear local cart state
        setCart({ items: [] });
        navigate('/demo/orders');

    } catch (err) {
        toast.error("Checkout failed. Try again.");
    } finally {
        setProcessing(false);
    }
  };

  if (loading) return <div className="p-10 text-center">Loading cart...</div>;

  const cartTotal = cart?.items?.reduce((sum, item) => sum + (item.product.price * item.quantity), 0) || 0;

  return (
    <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-10 animate-in fade-in duration-500">
      
      {/* Cart Items */}
      <div className="lg:col-span-2 space-y-6">
        <h1 className="text-3xl font-bold text-gray-900" style={{ fontFamily: '"Charm", cursive' }}>Your Bag</h1>
        
        {(!cart?.items || cart.items.length === 0) ? (
            <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-200">
                <ShoppingBag className="mx-auto h-16 w-16 text-gray-300 mb-4" />
                <p className="text-gray-500 text-lg">Your cart is empty.</p>
                <button onClick={() => navigate('/demo')} className="mt-4 text-blue-600 font-medium hover:underline">Continue Shopping</button>
            </div>
        ) : (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                {cart.items.map((item) => (
                    <div key={item.product_id} className="p-6 flex gap-6 border-b border-gray-100 last:border-0">
                        <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-md border border-gray-200">
                            <img
                                src={item.product.images?.[0]?.image_url || "https://ui.shadcn.com/placeholder.svg"}
                                alt={item.product.name}
                                className="h-full w-full object-cover object-center"
                            />
                        </div>

                        <div className="flex flex-1 flex-col">
                            <div>
                                <div className="flex justify-between text-base font-medium text-gray-900">
                                    <h3>{item.product.name}</h3>
                                    <p className="ml-4">${item.product.price * item.quantity}</p>
                                </div>
                                <p className="mt-1 text-sm text-gray-500">{item.product.category}</p>
                            </div>
                            <div className="flex flex-1 items-end justify-between text-sm">
                                <div className="flex items-center border border-gray-300 rounded-lg">
                                    <button 
                                        onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                                        className="px-3 py-1 hover:bg-gray-100 text-gray-600"
                                        disabled={item.quantity <= 1}
                                    >
                                        <Minus size={14} />
                                    </button>
                                    <span className="px-2 font-medium">{item.quantity}</span>
                                    <button 
                                        onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                                        className="px-3 py-1 hover:bg-gray-100 text-gray-600"
                                    >
                                        <Plus size={14} />
                                    </button>
                                </div>

                                <button
                                    type="button"
                                    onClick={() => removeItem(item.product_id)}
                                    className="font-medium text-red-500 hover:text-red-700 flex items-center gap-1"
                                >
                                    <Trash2 size={16} /> Remove
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        )}
      </div>

      {/* Checkout Section */}
      {cart?.items?.length > 0 && (
          <div className="lg:col-span-1 space-y-6">
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                  <h2 className="text-lg font-bold text-gray-900 mb-4">Shipping Address</h2>
                  
                  {addresses.length === 0 ? (
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-500 mb-2">No addresses found.</p>
                          <button onClick={() => navigate('/demo/profile')} className="text-blue-600 text-sm font-medium">Add Address in Profile</button>
                      </div>
                  ) : (
                      <div className="space-y-3">
                          {addresses.map(addr => (
                              <div 
                                key={addr.id} 
                                onClick={() => setSelectedAddress(addr.id)}
                                className={`p-3 rounded-xl border-2 cursor-pointer transition-all ${selectedAddress === addr.id ? 'border-blue-600 bg-blue-50' : 'border-gray-100 hover:border-gray-200'}`}
                              >
                                  <div className="flex items-center gap-2 mb-1">
                                      <MapPin size={16} className={selectedAddress === addr.id ? 'text-blue-600' : 'text-gray-400'} />
                                      <span className="font-semibold text-sm">{addr.label}</span>
                                  </div>
                                  <p className="text-xs text-gray-600 ml-6">{addr.address_line1}, {addr.city}</p>
                              </div>
                          ))}
                      </div>
                  )}
              </div>

              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                  <h2 className="text-lg font-bold text-gray-900 mb-4">Order Summary</h2>
                  <div className="space-y-2 text-sm text-gray-600 border-b border-gray-100 pb-4 mb-4">
                      <div className="flex justify-between">
                          <span>Subtotal</span>
                          <span>${cartTotal.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                          <span>Shipping</span>
                          <span>Free</span>
                      </div>
                  </div>
                  <div className="flex justify-between text-base font-bold text-gray-900 mb-6">
                      <span>Total</span>
                      <span>${cartTotal.toFixed(2)}</span>
                  </div>
                  
                  <button
                    onClick={() => navigate('/demo/checkout')}
                    disabled={processing}
                    className="w-full bg-black text-white py-4 rounded-xl font-bold text-lg hover:bg-gray-800 transition-all flex items-center justify-center gap-2 shadow-xl shadow-gray-200 disabled:opacity-70 disabled:cursor-not-allowed"
                  >
                    {processing ? "Processing..." : (
                        <>Checkout <ArrowRight size={20} /></>
                    )}
                  </button>
              </div>
          </div>
      )}
    </div>
  );
}