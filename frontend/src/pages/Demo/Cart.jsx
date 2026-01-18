import React, { useEffect, useState } from 'react';
import { api, analytics } from '../../lib/api';
import { ShoppingBag, Trash2, Plus, Minus, ArrowRight, Tag, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export default function Cart() {
  const [cart, setCart] = useState(null);
  const [offerPreview, setOfferPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      setLoading(true);
      const data = await api.get('/cart/');
      setCart(data);
      if (data.items.length > 0) {
        await fetchOffers();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchOffers = async () => {
    try {
      const data = await api.get('/cart/offers');
      setOfferPreview(data);
    } catch (e) {}
  };

  const updateQuantity = async (variantId, newQty) => {
    try {
      if (newQty <= 0) {
        await api.del(`/cart/items/${variantId}`);
        toast.success("Item removed");
      } else {
        await api.patch(`/cart/items/${variantId}`, { quantity: newQty });
      }
      fetchCart(); // Refetch to update totals/offers on backend
    } catch (err) {
      toast.error("Update failed");
    }
  };

  const clearCart = async () => {
    if(!confirm("Empty your cart?")) return;
    await api.del('/cart/');
    setCart(null);
    setOfferPreview(null);
  };

  if (loading) return <div className="p-20 flex justify-center"><Loader2 className="animate-spin text-gray-400"/></div>;

  if (!cart?.items || cart.items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-4 animate-in fade-in">
        <div className="bg-gray-100 p-6 rounded-full"><ShoppingBag size={48} className="text-gray-400"/></div>
        <h2 className="text-2xl font-bold text-gray-900">Your cart is empty</h2>
        <p className="text-gray-500">Looks like you haven't added anything yet.</p>
        <button onClick={() => navigate('/demo')} className="bg-gray-900 text-white px-8 py-3 rounded-xl font-medium hover:bg-black transition-all">Start Shopping</button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
         <h1 className="text-3xl font-bold font-serif">Your Bag <span className="text-gray-400 text-lg font-sans font-normal ml-2">({cart.items.length} items)</span></h1>
         <button onClick={clearCart} className="text-sm text-red-500 hover:text-red-700 font-medium">Clear Cart</button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-6">
          {cart.items.map((item) => (
            <div key={item.variant_id} className="flex gap-6 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-24 h-32 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                 <img src={item.variant?.images?.[0]?.image_url || item.product?.images?.[0]?.image_url || "https://ui.shadcn.com/placeholder.svg"} className="w-full h-full object-cover" alt="" />
              </div>
              
              <div className="flex-1 flex flex-col justify-between">
                <div>
                   <h3 className="text-lg font-bold text-gray-900">{item.product?.name}</h3>
                   <p className="text-gray-500 text-sm">{item.product?.category}</p>
                   {item.variant?.attributes && (
                     <div className="flex gap-2 mt-2">
                       {Object.entries(item.variant.attributes).map(([k,v]) => (
                         <span key={k} className="text-xs bg-gray-100 px-2 py-1 rounded capitalize">{k}: {v}</span>
                       ))}
                     </div>
                   )}
                </div>
                <div className="flex items-center justify-between mt-4">
                  <p className="font-bold text-lg">${item.variant?.price || item.product?.price}</p>
                  
                  <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-1 border border-gray-200">
                    <button onClick={() => updateQuantity(item.variant_id, item.quantity - 1)} className="p-1 hover:bg-white rounded shadow-sm"><Minus size={14}/></button>
                    <span className="text-sm font-semibold w-6 text-center">{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.variant_id, item.quantity + 1)} className="p-1 hover:bg-white rounded shadow-sm"><Plus size={14}/></button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="lg:col-span-1">
           <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-xl sticky top-24">
              <h2 className="text-xl font-bold mb-6">Order Summary</h2>
              
              <div className="space-y-4 text-sm text-gray-600 mb-6">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span className="font-medium text-gray-900">${offerPreview?.subtotal?.toFixed(2) || '0.00'}</span>
                </div>
                
                {offerPreview?.offers_applied?.map(offer => (
                   <div key={offer.id} className="flex justify-between text-green-600 bg-green-50 p-2 rounded">
                      <span className="flex items-center gap-1"><Tag size={12}/> {offer.title}</span>
                      <span>-{offer.amount_off || offer.percentage_off + '%'}</span>
                   </div>
                ))}
                
                <div className="flex justify-between pt-4 border-t border-gray-100 text-lg font-bold text-gray-900">
                  <span>Total</span>
                  <span>${offerPreview?.final_total?.toFixed(2) || offerPreview?.subtotal?.toFixed(2) || '0.00'}</span>
                </div>
              </div>

              <button 
                onClick={() => navigate('/demo/checkout')}
                className="w-full bg-gray-900 text-white py-4 rounded-xl font-bold text-lg hover:bg-black transition-all flex items-center justify-center gap-2 group"
              >
                Checkout <ArrowRight className="group-hover:translate-x-1 transition-transform"/>
              </button>
           </div>
        </div>
      </div>
    </div>
  );
}