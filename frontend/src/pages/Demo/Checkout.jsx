import React, { useEffect, useState, useMemo } from 'react';
import { apiRequest, analytics } from '../../lib/api';
import { toast } from 'sonner';
import { 
  MapPin, CreditCard, Truck, Store, ArrowRight, Loader2, 
  Check, X, Sparkles, Ticket, BadgePercent 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Checkout() {
  const [cart, setCart] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [offers, setOffers] = useState([]); // <--- New State for Offers
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const navigate = useNavigate();

  // Checkout State
  const [fulfillmentType, setFulfillmentType] = useState('delivery'); 
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [selectedStore, setSelectedStore] = useState(null);
  const [storeOptions, setStoreOptions] = useState([]);
  const [loadingStores, setLoadingStores] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (fulfillmentType === 'pickup' && cart?.items?.length > 0) {
        fetchStoreOptions();
    }
  }, [fulfillmentType, cart]);

  const fetchData = async () => {
    try {
      const [cartData, addressData, offersData] = await Promise.all([
        apiRequest('/cart/'),
        apiRequest('/addresses/'),
        apiRequest('/offers/') // <--- Fetch Offers
      ]);
      setCart(cartData);
      setAddresses(addressData);
      setOffers(offersData);

      const defaultAddr = addressData.find(a => a.is_default);
      if (defaultAddr) setSelectedAddress(defaultAddr.id);
    } catch (err) {
      console.error("Checkout init error", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStoreOptions = async () => {
      setLoadingStores(true);
      try {
          const productId = cart.items[0].product_id;
          let bestStoreId = null;

          // 1. Try Auto-Assign
          try {
              const bestStore = await apiRequest('/store/pickups/pickup/auto-store');
              if (bestStore) {
                  setStoreOptions([{
                      store_id: bestStore.store_id,
                      name: bestStore.name,
                      distance_m: bestStore.distance_m || 0,
                      stock: 'All Items Available',
                      is_best: true,
                      city: 'Auto-Matched'
                  }]);
                  setSelectedStore(bestStore.store_id);
                  bestStoreId = bestStore.store_id;
                  toast.success(`Matched store: ${bestStore.name}`);
              }
          } catch (e) {}

          // 2. Fetch Radius
          let stores = await apiRequest(`/stores/products/${productId}/nearest-stores?radius_km=100`);
          
          // 3. Fallback
          if (!stores || stores.length === 0) {
              const allStores = await apiRequest('/stores/');
              stores = allStores.map(s => ({
                  store_id: s.id,
                  name: s.name,
                  stock: 'Check availability', 
                  distance_m: null,
                  city: s.city
              }));
              if (stores.length > 0 && !bestStoreId) toast.info("Showing all locations.");
          }

          setStoreOptions(prev => {
              const newStores = stores.filter(s => s.store_id !== bestStoreId);
              return [...prev, ...newStores];
          });

          if (!bestStoreId && stores.length > 0) setSelectedStore(stores[0].store_id);

      } catch (err) {
          toast.error("Could not load store options");
      } finally {
          setLoadingStores(false);
      }
  };

  // --- LOGIC: Calculate Totals & Offers ---
  const { subtotal, discount, total, appliedOffers } = useMemo(() => {
      if (!cart?.items) return { subtotal: 0, discount: 0, total: 0, appliedOffers: [] };

      const sub = cart.items.reduce((acc, item) => acc + (item.product.price * item.quantity), 0);
      
      let totalDiscount = 0;
      const applied = [];

      // Replicate Backend Logic to show preview
      offers.forEach(offer => {
          const rules = offer.rules || {};
          let offerAmt = 0;

          // Check Min Value
          if (rules.min_cart_value && sub < parseFloat(rules.min_cart_value)) return;

          // Calc Discount
          if (rules.discount_percent) {
              offerAmt = sub * (parseFloat(rules.discount_percent) / 100);
          } else if (rules.discount_amount) {
              offerAmt = parseFloat(rules.discount_amount);
          }

          if (offerAmt > 0) {
              totalDiscount += offerAmt;
              applied.push({ ...offer, amount: offerAmt });
          }
      });

      // Ensure discount doesn't exceed subtotal
      totalDiscount = Math.min(totalDiscount, sub);

      return {
          subtotal: sub,
          discount: totalDiscount,
          total: sub - totalDiscount,
          appliedOffers: applied
      };
  }, [cart, offers]);


  const handlePayClick = () => {
      if (fulfillmentType === 'delivery' && !selectedAddress) return toast.error("Select an address");
      if (fulfillmentType === 'pickup' && !selectedStore) return toast.error("Select a store");
      setPaymentModalOpen(true);
  };

  const confirmPayment = async () => {
    setProcessing(true);
    try {
        await new Promise(r => setTimeout(r, 1500)); 

        const payload = {
            fulfillment_type: fulfillmentType,
            payment_provider: 'stripe_dummy',
            address_id: fulfillmentType === 'delivery' ? selectedAddress : null,
            store_id: fulfillmentType === 'pickup' ? selectedStore : null
        };

        const order = await apiRequest('/cart/checkout', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        analytics.track('order_created', { orderId: order.id, metadata: { total: order.total } });
        
        toast.success("Payment Successful!", { description: `Order #${order.id.slice(0,8)} placed.` });
        navigate(`/demo/orders/${order.id}`);

    } catch (err) {
        toast.error("Checkout Failed: " + (err.message || "Unknown error"));
        setPaymentModalOpen(false); 
    } finally {
        setProcessing(false);
    }
  };

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin text-gray-400"/></div>;
  if (!cart?.items?.length) return <div className="p-10 text-center">Cart empty.</div>;

  return (
    <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in duration-500 relative">
        
        {/* --- LEFT COLUMN --- */}
        <div className="lg:col-span-2 space-y-6">
            <h1 className="text-3xl font-bold text-gray-900" style={{ fontFamily: '"Charm", cursive' }}>Checkout</h1>
            
            {/* 1. Fulfillment */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h2 className="text-lg font-semibold mb-4">Delivery Method</h2>
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

            {/* 2. Address or Store */}
            {fulfillmentType === 'delivery' ? (
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm animate-in fade-in">
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
                        <button onClick={() => navigate('/demo/profile')} className="text-sm text-blue-600 font-medium w-fit">+ Add Address</button>
                    </div>
                </div>
            ) : (
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm animate-in fade-in">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Store size={18} /> Select Store</h2>
                    {loadingStores ? (
                        <div className="flex items-center gap-2 text-gray-500 p-4"><Loader2 className="animate-spin h-4 w-4"/> Locating optimal stores...</div>
                    ) : (
                        <div className="grid gap-3 max-h-60 overflow-y-auto pr-2">
                            {storeOptions.map(store => (
                                <div 
                                    key={store.store_id} 
                                    onClick={() => setSelectedStore(store.store_id)}
                                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all flex justify-between items-center ${selectedStore === store.store_id ? 'border-blue-600 bg-blue-50' : 'border-gray-100 hover:border-gray-300'}`}
                                >
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <p className="font-medium text-gray-900">{store.name}</p>
                                            {store.is_best && <span className="bg-amber-100 text-amber-700 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1"><Sparkles size={10}/> Best Match</span>}
                                        </div>
                                        <p className="text-xs text-gray-500">{store.city} {store.distance_m ? `• ${(store.distance_m / 1000).toFixed(1)} km` : ''}</p>
                                    </div>
                                    <span className={`text-xs px-2 py-1 rounded-full ${store.stock.includes('All') ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>{store.stock}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* 3. Offers Section */}
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Ticket size={18} className="text-purple-600" /> Available Offers
                </h2>
                {offers.length === 0 ? (
                    <p className="text-sm text-gray-500 italic">No offers available at this time.</p>
                ) : (
                    <div className="space-y-3">
                        {offers.map(offer => {
                            // Check if this specific offer is applied in our calculation
                            const isApplied = appliedOffers.some(ao => ao.id === offer.id);
                            
                            return (
                                <div key={offer.id} className={`p-4 border rounded-lg flex justify-between items-center ${isApplied ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50 opacity-70'}`}>
                                    <div className="flex items-start gap-3">
                                        <BadgePercent className={isApplied ? "text-green-600" : "text-gray-400"} size={20} />
                                        <div>
                                            <p className={`font-bold ${isApplied ? 'text-green-900' : 'text-gray-700'}`}>{offer.title}</p>
                                            <p className="text-xs text-gray-500">{offer.description}</p>
                                            {offer.rules?.min_cart_value && <p className="text-[10px] text-gray-400 mt-1">Min order: ${offer.rules.min_cart_value}</p>}
                                        </div>
                                    </div>
                                    {isApplied && (
                                        <div className="text-right">
                                            <span className="text-sm font-bold text-green-700">Applied</span>
                                            <Check size={16} className="text-green-600 ml-auto" />
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>

        {/* --- RIGHT COLUMN (SUMMARY) --- */}
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
                    
                    <div className="border-t border-gray-100 pt-3 space-y-2">
                        <div className="flex justify-between text-gray-600">
                            <span>Subtotal</span>
                            <span>${subtotal.toFixed(2)}</span>
                        </div>
                        {discount > 0 && (
                            <div className="flex justify-between text-green-600 font-medium">
                                <span>Discount</span>
                                <span>-${discount.toFixed(2)}</span>
                            </div>
                        )}
                        <div className="flex justify-between font-bold text-lg pt-2 border-t border-gray-100 mt-2">
                            <span>Total</span>
                            <span>${total.toFixed(2)}</span>
                        </div>
                    </div>
                </div>
                
                <button 
                    onClick={handlePayClick}
                    className="w-full bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-black transition-all flex items-center justify-center gap-2"
                >
                    Pay ${total.toFixed(2)} <ArrowRight size={18} />
                </button>
            </div>
        </div>

        {/* --- PAYMENT MODAL --- */}
        {paymentModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/60 backdrop-blur-sm animate-in fade-in">
                <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 relative">
                    <button onClick={() => !processing && setPaymentModalOpen(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
                        <X size={20} />
                    </button>
                    
                    <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                        <CreditCard className="text-blue-600"/> Secure Payment
                    </h2>

                    <div className="space-y-4 mb-6">
                        <div className="p-4 border rounded-xl bg-gray-50 flex items-center gap-4">
                            <div className="h-10 w-16 bg-white border rounded flex items-center justify-center">
                                <span className="font-bold text-blue-800 italic">VISA</span>
                            </div>
                            <div>
                                <p className="font-medium text-sm">**** **** **** 4242</p>
                                <p className="text-xs text-gray-500">Expires 12/28</p>
                            </div>
                            <Check className="ml-auto text-green-500" size={20} />
                        </div>
                        <div className="flex justify-between text-sm px-1">
                            <span className="text-gray-500">Total to pay</span>
                            <span className="font-bold text-lg">${total.toFixed(2)}</span>
                        </div>
                    </div>

                    <button 
                        onClick={confirmPayment}
                        disabled={processing}
                        className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
                    >
                        {processing ? <><Loader2 className="animate-spin" /> Processing...</> : "Confirm Payment"}
                    </button>
                </div>
            </div>
        )}
    </div>
  );
}