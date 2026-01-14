import React, { useEffect, useState } from 'react';
import { apiRequest, analytics } from '../../lib/api';
import { toast } from 'sonner';
import { MapPin, CreditCard, Truck, Store, ArrowRight, Loader2, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Checkout() {
  const [cart, setCart] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const navigate = useNavigate();

  // Checkout State
  const [fulfillmentType, setFulfillmentType] = useState('delivery'); // 'delivery' | 'pickup'
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [selectedStore, setSelectedStore] = useState(null);
  const [nearestStores, setNearestStores] = useState([]);
  const [loadingStores, setLoadingStores] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  // When switching to Pickup, find stores for the first item in cart
  useEffect(() => {
    if (fulfillmentType === 'pickup' && cart?.items?.length > 0) {
        findStores();
    }
  }, [fulfillmentType, cart]);

  const fetchData = async () => {
    try {
      const [cartData, addressData] = await Promise.all([
        apiRequest('/cart/'),
        apiRequest('/addresses/')
      ]);
      setCart(cartData);
      setAddresses(addressData);
      const defaultAddr = addressData.find(a => a.is_default);
      if (defaultAddr) setSelectedAddress(defaultAddr.id);
    } catch (err) {
      toast.error("Failed to init checkout");
    } finally {
      setLoading(false);
    }
  };

  const findStores = async () => {
      setLoadingStores(true);
      try {
          // Use the first product to find stores
          const productId = cart.items[0].product_id;
          const stores = await apiRequest(`/stores/products/${productId}/nearest-stores?radius_km=50`);
          setNearestStores(stores);
      } catch (err) {
          toast.error("Could not find nearby stores");
      } finally {
          setLoadingStores(false);
      }
  };

  const handlePlaceOrder = async () => {
    setProcessing(true);
    try {
        const payload = {
            fulfillment_type: fulfillmentType,
            payment_provider: 'stripe_dummy',
            address_id: fulfillmentType === 'delivery' ? selectedAddress : null,
            store_id: fulfillmentType === 'pickup' ? selectedStore : null
        };

        if (fulfillmentType === 'delivery' && !payload.address_id) throw new Error("Select an address");
        if (fulfillmentType === 'pickup' && !payload.store_id) throw new Error("Select a store");

        const order = await apiRequest('/cart/checkout', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        analytics.track('order_created', { orderId: order.id, metadata: { total: order.total, type: fulfillmentType } });
        
        toast.success(`Order #${order.id.slice(0,8)} Confirmed!`);
        navigate(`/demo/orders`);

    } catch (err) {
        toast.error("Checkout Failed: " + err.message);
    } finally {
        setProcessing(false);
    }
  };

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin text-gray-400"/></div>;
  if (!cart?.items?.length) return <div className="p-10 text-center">Cart empty.</div>;

  const total = cart.items.reduce((acc, item) => acc + (item.product.price * item.quantity), 0);

  return (
    <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in duration-500">
        <div className="lg:col-span-2 space-y-8">
            <h1 className="text-3xl font-bold text-gray-900" style={{ fontFamily: '"Charm", cursive' }}>Checkout</h1>
            
            {/* 1. Fulfillment Method */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h2 className="text-lg font-semibold mb-4">How do you want your order?</h2>
                <div className="grid grid-cols-2 gap-4">
                    <button 
                        onClick={() => setFulfillmentType('delivery')}
                        className={`p-4 rounded-xl border-2 flex flex-col items-center gap-2 transition-all ${fulfillmentType === 'delivery' ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-100 hover:border-gray-300'}`}
                    >
                        <Truck size={24} />
                        <span className="font-medium">Home Delivery</span>
                    </button>
                    <button 
                        onClick={() => setFulfillmentType('pickup')}
                        className={`p-4 rounded-xl border-2 flex flex-col items-center gap-2 transition-all ${fulfillmentType === 'pickup' ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-100 hover:border-gray-300'}`}
                    >
                        <Store size={24} />
                        <span className="font-medium">Store Pickup</span>
                    </button>
                </div>
            </div>

            {/* 2. Delivery Address OR Store Selection */}
            {fulfillmentType === 'delivery' ? (
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm animate-in fade-in slide-in-from-top-2">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><MapPin size={18} /> Shipping Address</h2>
                    <div className="grid gap-3">
                        {addresses.map(addr => (
                            <div 
                                key={addr.id} 
                                onClick={() => setSelectedAddress(addr.id)}
                                className={`p-4 rounded-lg border-2 cursor-pointer transition-all flex items-start gap-3 ${selectedAddress === addr.id ? 'border-blue-600 bg-blue-50' : 'border-gray-100 hover:border-gray-300'}`}
                            >
                                <div className={`mt-1 h-4 w-4 rounded-full border flex items-center justify-center ${selectedAddress === addr.id ? 'border-blue-600' : 'border-gray-400'}`}>
                                    {selectedAddress === addr.id && <div className="h-2 w-2 rounded-full bg-blue-600" />}
                                </div>
                                <div>
                                    <p className="font-medium text-gray-900">{addr.label}</p>
                                    <p className="text-sm text-gray-500">{addr.address_line1}, {addr.city}</p>
                                </div>
                            </div>
                        ))}
                        <button onClick={() => navigate('/demo/profile')} className="text-sm text-blue-600 font-medium">+ Add Address</button>
                    </div>
                </div>
            ) : (
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm animate-in fade-in slide-in-from-top-2">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Store size={18} /> Select Store</h2>
                    {loadingStores ? (
                        <div className="flex items-center gap-2 text-gray-500"><Loader2 className="animate-spin h-4 w-4"/> Finding nearest stores...</div>
                    ) : nearestStores.length === 0 ? (
                        <p className="text-red-500 text-sm">No stores with stock found nearby.</p>
                    ) : (
                        <div className="grid gap-3">
                            {nearestStores.map(store => (
                                <div 
                                    key={store.store_id} 
                                    onClick={() => setSelectedStore(store.store_id)}
                                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all flex justify-between items-center ${selectedStore === store.store_id ? 'border-blue-600 bg-blue-50' : 'border-gray-100 hover:border-gray-300'}`}
                                >
                                    <div>
                                        <p className="font-medium text-gray-900">{store.name}</p>
                                        <p className="text-xs text-gray-500">{(store.distance_m / 1000).toFixed(1)} km away</p>
                                    </div>
                                    <div className="text-right">
                                        <span className="block text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
                                            {store.stock} in stock
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* 3. Payment */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><CreditCard size={18} /> Payment</h2>
                <div className="p-4 rounded-lg border border-blue-100 bg-blue-50 flex items-center gap-3">
                    <div className="bg-white p-2 rounded border border-gray-200"><CreditCard className="text-blue-600" /></div>
                    <div>
                        <p className="font-medium text-gray-900">Demo Card •••• 4242</p>
                    </div>
                    <Check className="ml-auto text-blue-600 h-5 w-5" />
                </div>
            </div>
        </div>

        {/* Summary Side */}
        <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-lg sticky top-24">
                <h2 className="text-lg font-bold mb-4">Order Summary</h2>
                <div className="space-y-3 mb-6">
                    {cart.items.map(item => (
                        <div key={item.product_id} className="flex justify-between text-sm">
                            <span className="text-gray-600 truncate max-w-[150px]">{item.product.name} (x{item.quantity})</span>
                            <span className="font-medium">${(item.product.price * item.quantity).toFixed(2)}</span>
                        </div>
                    ))}
                    <div className="border-t border-gray-100 pt-3 flex justify-between font-bold text-lg">
                        <span>Total</span>
                        <span>${total.toFixed(2)}</span>
                    </div>
                </div>
                
                <button 
                    onClick={handlePlaceOrder}
                    disabled={processing || (fulfillmentType === 'delivery' && !selectedAddress) || (fulfillmentType === 'pickup' && !selectedStore)}
                    className="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-black transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {processing ? <Loader2 className="animate-spin" /> : <>Pay ${total.toFixed(2)} <ArrowRight size={18} /></>}
                </button>
            </div>
        </div>
    </div>
  );
}