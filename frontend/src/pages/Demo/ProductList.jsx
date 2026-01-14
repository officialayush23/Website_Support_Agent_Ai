import React, { useEffect, useMemo, useState } from 'react';
import { apiRequest, analytics } from '../../lib/api';
import { ShoppingBag, X, Star, Check, ChevronLeft, ChevronRight, Search } from 'lucide-react';
import { toast } from "sonner"

// --- Components ---

const ProductCard = ({ product, onOpen, onAdd }) => {
  const mainImage = product.images?.find(img => img.is_primary)?.image_url || product.images?.[0]?.image_url || "https://ui.shadcn.com/placeholder.svg";

  return (
    <div className="group relative animate-in fade-in zoom-in-95 duration-500">
      <div 
        onClick={() => onOpen(product)}
        className="aspect-[3/4] w-full overflow-hidden rounded-xl bg-gray-100 cursor-pointer relative"
      >
        <img
          src={mainImage}
          alt={product.name}
          className="h-full w-full object-cover object-center transition-transform duration-700 group-hover:scale-105"
        />
        <div className="absolute inset-x-0 bottom-0 p-4 opacity-0 translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAdd(product);
            }}
            className="w-full bg-white/95 backdrop-blur-sm text-gray-900 font-medium py-3 rounded-lg shadow-lg hover:bg-white transition-colors flex items-center justify-center gap-2"
          >
            <ShoppingBag size={18} />
            Add to Cart
          </button>
        </div>
      </div>
      <div className="mt-4 flex justify-between">
        <div>
          <h3 className="text-sm text-gray-700 font-medium cursor-pointer hover:text-blue-600 transition-colors" onClick={() => onOpen(product)}>
            {product.name}
          </h3>
          <p className="mt-1 text-sm text-gray-500">{product.category}</p>
        </div>
        <p className="text-sm font-semibold text-gray-900">${product.price}</p>
      </div>
    </div>
  );
};

const ProductModal = ({ product, isOpen, onClose, onAdd }) => {
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  useEffect(() => {
    if (isOpen) setActiveImageIndex(0); // Reset on open
  }, [isOpen]);

  if (!isOpen || !product) return null;

  // Gather images or use placeholder
  const images = product.images && product.images.length > 0 
    ? product.images 
    : [{ image_url: "https://ui.shadcn.com/placeholder.svg", id: 'placeholder' }];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" onClick={onClose} />
      
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-5xl overflow-hidden flex flex-col md:flex-row animate-in fade-in zoom-in-95 duration-200 max-h-[90vh]">
        <button onClick={onClose} className="absolute top-4 right-4 p-2 bg-white/80 hover:bg-white rounded-full z-10 transition-colors">
          <X size={20} />
        </button>

        {/* Gallery Side */}
        <div className="w-full md:w-1/2 bg-gray-50 relative flex flex-col">
           {/* Main Image */}
           <div className="flex-1 relative overflow-hidden">
              <img
                src={images[activeImageIndex].image_url}
                alt={product.name}
                className="w-full h-full object-cover object-center absolute inset-0"
              />
              
              {/* Arrows if multiple images */}
              {images.length > 1 && (
                  <>
                    <button 
                        onClick={() => setActiveImageIndex(i => i === 0 ? images.length - 1 : i - 1)}
                        className="absolute left-4 top-1/2 -translate-y-1/2 p-2 bg-white/80 hover:bg-white rounded-full shadow-sm"
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <button 
                        onClick={() => setActiveImageIndex(i => i === images.length - 1 ? 0 : i + 1)}
                        className="absolute right-4 top-1/2 -translate-y-1/2 p-2 bg-white/80 hover:bg-white rounded-full shadow-sm"
                    >
                        <ChevronRight size={20} />
                    </button>
                  </>
              )}
           </div>

           {/* Thumbnails */}
           {images.length > 1 && (
               <div className="p-4 flex gap-2 overflow-x-auto bg-white border-t border-gray-100 no-scrollbar">
                   {images.map((img, idx) => (
                       <button 
                        key={img.id}
                        onClick={() => setActiveImageIndex(idx)}
                        className={`w-16 h-16 flex-shrink-0 rounded-lg overflow-hidden border-2 transition-all ${
                            activeImageIndex === idx ? 'border-blue-600 opacity-100' : 'border-transparent opacity-60 hover:opacity-100'
                        }`}
                       >
                           <img src={img.image_url} className="w-full h-full object-cover" alt="thumbnail" />
                       </button>
                   ))}
               </div>
           )}
        </div>

        {/* Details Side */}
        <div className="w-full md:w-1/2 p-8 md:p-12 flex flex-col overflow-y-auto">
          <div className="mb-6">
            <span className="inline-block px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-xs font-semibold tracking-wide uppercase mb-3">
              {product.category || 'Collection'}
            </span>
            <h2 className="text-3xl font-bold text-gray-900 mb-2 font-serif">{product.name}</h2>
            <div className="flex items-center gap-2 mb-4">
              <div className="flex text-yellow-400">
                {[...Array(5)].map((_, i) => <Star key={i} size={16} fill="currentColor" />)}
              </div>
              <span className="text-sm text-gray-500">(4.8 Stars)</span>
            </div>
            <p className="text-gray-600 leading-relaxed text-lg">
              {product.description || "Designed for modern living, this piece combines elegance with everyday functionality."}
            </p>
          </div>

          <div className="mt-auto pt-8">
             <div className="flex items-center justify-between mb-6">
                <span className="text-4xl font-bold text-gray-900">${product.price}</span>
                <span className="text-sm text-green-600 font-medium flex items-center gap-1 bg-green-50 px-3 py-1 rounded-full">
                  <Check size={16} /> In Stock
                </span>
             </div>

             <button
              onClick={() => onAdd(product)}
              className="w-full bg-gray-900 text-white py-4 rounded-xl font-semibold hover:bg-gray-800 transition-all flex items-center justify-center gap-2 shadow-xl shadow-gray-200 hover:shadow-gray-300 transform hover:-translate-y-0.5"
            >
              <ShoppingBag size={20} />
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [offers, setOffers] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');

 
  useEffect(() => {
    fetchProducts();
    fetchOffers();
    fetchData(); // <--- NEW
  }, []);

  const fetchData = async () => {
    try {
      const [prodData, offerData] = await Promise.all([
          apiRequest('/products/'),
          apiRequest('/offers/')
      ]);
      setProducts(prodData);
      setOffers(offerData);
    } catch (err) {
      toast.error("Failed to load shop");
    } finally {
      setLoading(false);
    }
  };

  const fetchOffers = async () => {
      try {
          const data = await apiRequest('/offers/');
          setOffers(data);
      } catch (err) { console.error(err); }
  }


  const fetchProducts = async () => {
    try {
      const data = await apiRequest('/products/');
      setProducts(data);
    } catch (err) {
      toast.error("Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = useMemo(() => {
      return products.filter(p => {
          const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase());
          const matchesCat = category === 'All' || p.category === category;
          return matchesSearch && matchesCat;
      });
  }, [products, search, category]);

  // Unique Categories
  const categories = ['All', ...new Set(products.map(p => p.category).filter(Boolean))];

  const handleOpenProduct = (product) => {
    setSelectedProduct(product);
    analytics.track('view_product', {
      productId: product.id,
      metadata: { name: product.name, price: product.price, category: product.category }
    });
  };

  const handleAddToCart = async (product) => {
    try {
      await apiRequest('/cart/items', {
        method: 'POST',
        body: JSON.stringify({ product_id: product.id, quantity: 1 })
      });

      analytics.track('add_to_cart', {
        productId: product.id,
        metadata: { price: product.price, name: product.name }
      });
      
      // ✅ Sonner Toast
      toast.success(`${product.name} added to cart`, {
        description: "Great choice! Check your cart to checkout.",
        action: {
            label: "View Cart",
            onClick: () => console.log("Navigate to cart") // You can hook navigate here
        }
      });

    } catch (err) {
      toast.error("Failed to add item to cart");
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-10">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="aspect-[3/4] bg-gray-200 rounded-xl mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-10 flex justify-between items-end">
        <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight" style={{ fontFamily: '"Charm", cursive' }}>New Collection</h1>
            <p className="text-gray-500 mt-2">Discover the latest trends picked just for you.</p>
        </div>
      </div>

      {offers.length > 0 && (
          <div className="mb-8 grid gap-4 md:grid-cols-2">
              {offers.map(offer => (
                  <div key={offer.id} className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white shadow-lg relative overflow-hidden">
                      <div className="relative z-10">
                          <span className="bg-white/20 backdrop-blur-md px-2 py-1 rounded text-xs font-bold uppercase tracking-wider mb-2 inline-block">Limited Offer</span>
                          <h3 className="text-2xl font-bold mb-1">{offer.title}</h3>
                          <p className="text-blue-100 text-sm">{offer.description}</p>
                      </div>
                      <div className="absolute right-0 top-0 h-full w-32 bg-white/10 -skew-x-12 transform translate-x-8"></div>
                  </div>
              ))}
          </div>
      )}
      <div className="mb-8 flex flex-col md:flex-row justify-between items-end gap-4">
        <div>
            <h1 className="text-3xl font-bold text-gray-900" style={{ fontFamily: '"Charm", cursive' }}>Collection</h1>
            <p className="text-gray-500 mt-1">{filteredProducts.length} items found</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input 
                    type="text" 
                    placeholder="Search..." 
                    className="pl-9 pr-4 py-2 border rounded-lg text-sm w-full focus:outline-none focus:border-blue-500"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
            </div>
            <div className="flex gap-2 overflow-x-auto no-scrollbar">
                {categories.map(cat => (
                    <button 
                        key={cat}
                        onClick={() => setCategory(cat)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${category === cat ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                    >
                        {cat}
                    </button>
                ))}
            </div>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-x-4 gap-y-8 sm:gap-x-6 sm:gap-y-10">
        {products.map((product) => (
          <ProductCard 
            key={product.id} 
            product={product} 
            onOpen={handleOpenProduct}
            onAdd={handleAddToCart}
          />
        ))}
      </div>

      <ProductModal 
        product={selectedProduct} 
        isOpen={!!selectedProduct} 
        onClose={() => setSelectedProduct(null)} 
        onAdd={(p) => {
            handleAddToCart(p);
            setSelectedProduct(null);
        }}
      />
    </div>
  );
}