import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../../lib/api';
import { toast } from 'sonner';
import { Box, Save, RefreshCw, Search, Globe, Store as StoreIcon, ArrowRight, Loader2 } from 'lucide-react';

export default function AdminInventory() {
  const [catalog, setCatalog] = useState([]);
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  // Selection
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  // Forms
  const [globalStockInput, setGlobalStockInput] = useState(0);
  const [storeStock, setStoreStock] = useState({ storeId: '', quantity: 0 });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [catalogData, storesData] = await Promise.all([
        apiRequest('/stores/admin/catalog'), // Uses the new endpoint which returns total_stock
        apiRequest('/stores/')
      ]);
      setCatalog(catalogData);
      setStores(storesData);
    } catch (err) {
      console.warn("Inventory fetch warning:", err);
      // fallback
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProduct = (product) => {
      setSelectedProduct(product);
      // Use data directly from catalog list instead of fetching separate endpoint that was failing
      setGlobalStockInput(product.total_stock || 0); 
      setStoreStock({ storeId: '', quantity: 0 });
  };

  const handleUpdateGlobal = async () => {
      setSubmitting(true);
      try {
          await apiRequest('/stores/admin/global-stock', {
              method: 'PATCH',
              body: JSON.stringify({
                  product_id: selectedProduct.product_id, // Ensure this key matches backend expectation
                  total_stock: parseInt(globalStockInput)
              })
          });
          toast.success("Global stock updated");
          
          setCatalog(prev => prev.map(p => 
            (p.product_id === selectedProduct.product_id) 
            ? { ...p, total_stock: parseInt(globalStockInput) } 
            : p
          ));
      } catch (err) {
          toast.error("Failed to update global stock");
      } finally {
          setSubmitting(false);
      }
  };

  const handleUpdateStore = async () => {
      if (!storeStock.storeId) return toast.error("Select a store");
      setSubmitting(true);
      try {
          await apiRequest('/stores/admin/inventory', {
              method: 'PATCH',
              body: JSON.stringify({
                  store_id: storeStock.storeId,
                  product_id: selectedProduct.product_id, // Ensure using correct ID key from catalog list
                  stock: parseInt(storeStock.quantity)
              })
          });
          toast.success("Store inventory updated");
      } catch (err) {
          toast.error("Failed to update store stock");
      } finally {
          setSubmitting(false);
      }
  };

  const filteredCatalog = catalog.filter(p => p.name.toLowerCase().includes(search.toLowerCase()));

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin text-gray-400" /></div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 h-[calc(100vh-140px)]">
      <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Inventory Catalog</h1>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
          
          {/* Left: Catalog List */}
          <div className="lg:col-span-1 bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col h-full overflow-hidden">
              <div className="p-4 border-b border-gray-100 bg-gray-50/50">
                  <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <input 
                        type="text" 
                        placeholder="Search products..." 
                        className="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                      />
                  </div>
              </div>
              <div className="flex-1 overflow-y-auto p-2 space-y-1">
                  {filteredCatalog.map(p => (
                      <button
                        key={p.product_id}
                        onClick={() => handleSelectProduct(p)}
                        className={`w-full text-left p-3 rounded-lg flex items-center gap-3 transition-colors ${
                            selectedProduct?.product_id === p.product_id
                                ? 'bg-blue-50 border-blue-200 ring-1 ring-blue-200' 
                                : 'hover:bg-gray-50'
                        }`}
                      >
                          <div className="h-10 w-10 rounded bg-gray-100 overflow-hidden flex-shrink-0 border border-gray-200">
                              <img src={p.image || "https://ui.shadcn.com/placeholder.svg"} alt="" className="h-full w-full object-cover" />
                          </div>
                          <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 truncate">{p.name}</p>
                              <div className="flex items-center gap-2 mt-0.5">
                                <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${p.total_stock > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                    {p.total_stock} Global
                                </span>
                                <span className="text-[10px] text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">${p.price}</span>
                              </div>
                          </div>
                          {selectedProduct?.product_id === p.product_id && <ArrowRight className="ml-auto h-4 w-4 text-blue-500" />}
                      </button>
                  ))}
              </div>
          </div>

          {/* Right: Management Panel */}
          <div className="lg:col-span-2 space-y-6">
              {selectedProduct ? (
                  <>
                      {/* Product Header */}
                      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
                          <div className="h-20 w-20 rounded-lg bg-gray-100 overflow-hidden border border-gray-200">
                               <img src={selectedProduct.image || "https://ui.shadcn.com/placeholder.svg"} alt="" className="h-full w-full object-cover" />
                          </div>
                          <div>
                              <h2 className="text-xl font-bold text-gray-900">{selectedProduct.name}</h2>
                              <p className="text-gray-500 text-sm flex items-center gap-2">
                                  {selectedProduct.category} 
                                  <span className="text-gray-300">•</span> 
                                  ID: {selectedProduct.product_id.slice(0,8)}...
                              </p>
                          </div>
                      </div>

                      {/* Global Stock Card */}
                      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                          <div className="flex items-center gap-2 mb-4">
                              <div className="p-2 bg-blue-50 rounded-lg text-blue-600"><Globe size={20} /></div>
                              <div>
                                <h3 className="font-bold text-gray-900">Global Supply Chain</h3>
                                <p className="text-xs text-gray-500">Central warehouse stock definition</p>
                              </div>
                          </div>
                          
                          <div className="flex items-end gap-4 p-4 bg-gray-50 rounded-lg border border-gray-100">
                              <div className="flex-1">
                                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Total Global Stock</label>
                                  <input 
                                    type="number" 
                                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all" 
                                    value={globalStockInput}
                                    onChange={e => setGlobalStockInput(e.target.value)}
                                  />
                              </div>
                              <button 
                                onClick={handleUpdateGlobal}
                                disabled={submitting}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 transition-colors font-medium shadow-sm"
                              >
                                  {submitting ? <Loader2 className="animate-spin h-4 w-4" /> : <Save size={16} />}
                                  Update Global
                              </button>
                          </div>
                          <div className="mt-3 flex gap-4 text-xs text-gray-500">
                              <span>Reserved: <b className="text-gray-900">{selectedProduct.reserved_stock || 0}</b></span>
                              <span>Available to Allocate: <b className="text-gray-900">{Math.max(0, globalStockInput - (selectedProduct.reserved_stock || 0))}</b></span>
                          </div>
                      </div>

                      {/* Store Allocation Card */}
                      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                          <div className="flex items-center gap-2 mb-4">
                              <div className="p-2 bg-orange-50 rounded-lg text-orange-600"><StoreIcon size={20} /></div>
                              <div>
                                <h3 className="font-bold text-gray-900">Store Allocation</h3>
                                <p className="text-xs text-gray-500">Distribute stock to physical locations</p>
                              </div>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-4 mb-4">
                              <div>
                                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Select Store</label>
                                  <select 
                                    className="w-full p-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                    value={storeStock.storeId}
                                    onChange={e => setStoreStock({...storeStock, storeId: e.target.value})}
                                  >
                                      <option value="">-- Choose Store --</option>
                                      {stores.map(s => <option key={s.id} value={s.id}>{s.name} ({s.city})</option>)}
                                  </select>
                              </div>
                              <div>
                                  <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Local Stock Quantity</label>
                                  <input 
                                    type="number" 
                                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                    value={storeStock.quantity}
                                    onChange={e => setStoreStock({...storeStock, quantity: e.target.value})}
                                  />
                              </div>
                          </div>
                          <div className="flex justify-end">
                              <button 
                                onClick={handleUpdateStore}
                                disabled={submitting}
                                className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 flex items-center gap-2 transition-colors font-medium shadow-sm"
                              >
                                  {submitting ? <Loader2 className="animate-spin h-4 w-4" /> : <RefreshCw size={16} />}
                                  Update Store Inventory
                              </button>
                          </div>
                      </div>
                  </>
              ) : (
                  <div className="h-full flex flex-col items-center justify-center text-gray-400 border-2 border-dashed border-gray-200 rounded-xl bg-gray-50/50">
                      <Box size={48} className="mb-4 opacity-50" />
                      <p>Select a product from the catalog to manage its inventory.</p>
                  </div>
              )}
          </div>
      </div>
    </div>
  );
}