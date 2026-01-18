// frontend/src/pages/Demo/Admin/AdminProductList.jsx
import React, { useEffect, useState, useRef } from 'react';
import { apiRequest } from '../../../lib/api';
import { supabase } from '../../../lib/supabase';
import { 
  Plus, Package, Trash2, Loader2, Image as ImageIcon, 
  Upload, X, MoreHorizontal, CheckCircle 
} from 'lucide-react';
import { toast } from 'sonner';

export default function AdminProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('products');
  
  // --- Create Product State ---
  const [showAddModal, setShowAddModal] = useState(false);
  const [newProduct, setNewProduct] = useState({ name: '', price: '', category: '', description: '' });
  const [createFiles, setCreateFiles] = useState([]); // 
  const [isSubmitting, setIsSubmitting] = useState(false);

  // --- Manage Images State ---
  const [managingImagesFor, setManagingImagesFor] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await apiRequest('/products/');
      setProducts(data);
    } catch (err) {
      toast.error("Failed to fetch products");
    } finally {
      setLoading(false);
    }
  };

  // --- Create Product with Images Flow ---
  const handleCreateProduct = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    const toastId = toast.loading("Creating product...");

    try {
      // 1. Create the Product Entity
      const productRes = await apiRequest('/admin/products', {
        method: 'POST',
        body: JSON.stringify({
          ...newProduct,
          price: parseFloat(newProduct.price),
          attributes: {} 
        })
      });

      // 2. Upload Images (if any)
      if (createFiles.length > 0) {
        toast.loading(`Uploading ${createFiles.length} images...`, { id: toastId });
        
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;

        // Upload sequentially to ensure order (optional, could be Promise.all)
        for (let i = 0; i < createFiles.length; i++) {
            const formData = new FormData();
            formData.append('file', createFiles[i]);
            
            // First image selected is Primary
            const isPrimary = i === 0; 

            // Note the trailing slash in URL
            await fetch(
                `${import.meta.env.VITE_API_URL}/admin/products/images/?product_id=${productRes.id}&is_primary=${isPrimary}`, 
                {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                }
            );
        }
      }

      toast.success("Product created successfully", { id: toastId });
      
      // Reset & Refresh
      setShowAddModal(false);
      setNewProduct({ name: '', price: '', category: '', description: '' });
      setCreateFiles([]);
      fetchData();

    } catch (err) {
      toast.error("Failed: " + err.message, { id: toastId });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteProduct = async (id) => {
    if(!confirm("Delete this product and all its history?")) return;
    try {
      await apiRequest(`/admin/products/${id}`, { method: 'DELETE' });
      setProducts(products.filter(p => p.id !== id));
      toast.success("Product deleted");
    } catch (err) {
      toast.error("Failed to delete");
    }
  };

  // --- Image Manager Logic ---
  const handleUploadSingleImage = async (e) => {
    const file = e.target.files[0];
    if (!file || !managingImagesFor) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;

        const response = await fetch(
            `${import.meta.env.VITE_API_URL}/admin/products/images/?product_id=${managingImagesFor.id}&is_primary=${managingImagesFor.images?.length === 0}`, 
            {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            }
        );

        if (!response.ok) throw new Error("Upload failed");
        
        toast.success("Image uploaded");
        
        // Refresh local view
        const updatedProduct = await apiRequest(`/products/${managingImagesFor.id}`);
        setManagingImagesFor(updatedProduct);
        // Update main list
        setProducts(products.map(p => p.id === updatedProduct.id ? updatedProduct : p));

    } catch (err) {
        toast.error("Upload failed");
    } finally {
        setUploading(false);
    }
  };

  const handleDeleteImage = async (imageId) => {
      try {
          await apiRequest(`/admin/products/images/${imageId}`, { method: 'DELETE' });
          
          const updatedImages = managingImagesFor.images.filter(img => img.id !== imageId);
          const updatedProduct = { ...managingImagesFor, images: updatedImages };
          
          setManagingImagesFor(updatedProduct);
          setProducts(products.map(p => p.id === managingImagesFor.id ? updatedProduct : p));
          
          toast.success("Image removed");
      } catch (err) {
          toast.error("Failed to remove image");
      }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight" style={{ fontFamily: '"Charm", cursive' }}>Admin Console</h1>
          <p className="text-gray-500 mt-1">Manage catalog, inventory, and visual assets.</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="bg-gray-900 text-white px-5 py-2.5 rounded-xl shadow-lg hover:bg-gray-800 transition-all flex items-center gap-2 font-medium"
        >
          <Plus size={18} /> New Product
        </button>
      </div>

      {/* Product List */}
      {loading ? (
        <div className="flex justify-center py-20"><Loader2 className="animate-spin text-gray-400 h-8 w-8" /></div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-100">
            <thead className="bg-gray-50/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Product</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Category</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Price</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Assets</th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {products.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50/80 transition-colors group">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-12 w-12 flex-shrink-0 bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                        <img className="h-full w-full object-cover" src={product.images?.[0]?.image_url || "https://ui.shadcn.com/placeholder.svg"} alt="" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{product.name}</div>
                        <div className="text-xs text-gray-500 truncate max-w-[150px]">{product.description}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2.5 py-1 inline-flex text-xs leading-5 font-medium rounded-full bg-gray-100 text-gray-600">
                      {product.category || 'General'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${product.price}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex -space-x-2 overflow-hidden">
                        {product.images?.slice(0,3).map(img => (
                            <img key={img.id} className="inline-block h-6 w-6 rounded-full ring-2 ring-white object-cover" src={img.image_url} alt=""/>
                        ))}
                        {(product.images?.length || 0) > 3 && (
                            <span className="inline-block h-6 w-6 rounded-full ring-2 ring-white bg-gray-100 flex items-center justify-center text-[9px] text-gray-500">+{product.images.length - 3}</span>
                        )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => setManagingImagesFor(product)} className="text-gray-500 hover:text-blue-600 bg-white border border-gray-200 hover:border-blue-200 p-2 rounded-lg transition-all" title="Manage Images">
                            <ImageIcon size={16} />
                        </button>
                        <button onClick={() => handleDeleteProduct(product.id)} className="text-gray-500 hover:text-red-600 bg-white border border-gray-200 hover:border-red-200 p-2 rounded-lg transition-all" title="Delete">
                            <Trash2 size={16} />
                        </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* --- CREATE MODAL --- */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/40 backdrop-blur-sm p-4">
           <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-8 animate-in zoom-in-95 border border-white/20">
              <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Add Product</h2>
                  <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600"><X /></button>
              </div>
              
              <form onSubmit={handleCreateProduct} className="space-y-5">
                 {/* Image Drag & Drop Area */}
                 <div className="border-2 border-dashed border-gray-200 rounded-xl p-6 flex flex-col items-center justify-center text-center hover:bg-gray-50 transition-colors relative">
                    <input 
                        type="file" 
                        multiple 
                        accept="image/*"
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        onChange={(e) => setCreateFiles(Array.from(e.target.files))}
                    />
                    <div className="bg-blue-50 p-3 rounded-full mb-3">
                        <Upload className="h-6 w-6 text-blue-500" />
                    </div>
                    {createFiles.length > 0 ? (
                        <div>
                            <p className="text-sm font-medium text-gray-900">{createFiles.length} files selected</p>
                            <p className="text-xs text-gray-500 mt-1">{createFiles[0].name} {createFiles.length > 1 && `+ ${createFiles.length - 1} more`}</p>
                        </div>
                    ) : (
                        <div>
                            <p className="text-sm font-medium text-gray-900">Upload Product Images</p>
                            <p className="text-xs text-gray-500 mt-1">Drag & drop or click to select multiple</p>
                        </div>
                    )}
                 </div>

                 <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Product Name</label>
                        <input required className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-gray-900 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" 
                          placeholder="e.g. Silk Summer Dress"
                          value={newProduct.name} onChange={e => setNewProduct({...newProduct, name: e.target.value})} />
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Price</label>
                        <input required type="number" step="0.01" className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-gray-900 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" 
                          placeholder="0.00"
                          value={newProduct.price} onChange={e => setNewProduct({...newProduct, price: e.target.value})} />
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Category</label>
                        <input required className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-gray-900 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" 
                          placeholder="e.g. Dresses"
                          value={newProduct.category} onChange={e => setNewProduct({...newProduct, category: e.target.value})} />
                    </div>
                    <div className="col-span-2">
                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Description</label>
                        <textarea className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-gray-900 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all" rows="3"
                          placeholder="Product details..."
                          value={newProduct.description} onChange={e => setNewProduct({...newProduct, description: e.target.value})} />
                    </div>
                 </div>

                 <button type="submit" disabled={isSubmitting} className="w-full bg-gray-900 hover:bg-gray-800 text-white font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2">
                    {isSubmitting ? <Loader2 className="animate-spin" /> : 'Create Product'}
                 </button>
              </form>
           </div>
        </div>
      )}

      {/* --- MANAGE IMAGES MODAL --- */}
      {managingImagesFor && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl p-6 animate-in zoom-in-95 overflow-hidden flex flex-col max-h-[85vh]">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-xl font-bold">Product Gallery</h2>
                        <p className="text-sm text-gray-500">Managing assets for <span className="font-medium text-gray-900">{managingImagesFor.name}</span></p>
                    </div>
                    <button onClick={() => setManagingImagesFor(null)} className="p-2 hover:bg-gray-100 rounded-full"><X /></button>
                </div>

                <div className="flex-1 overflow-y-auto mb-6">
                    <div className="grid grid-cols-3 sm:grid-cols-4 gap-4">
                        {/* Upload Tile */}
                        <label className="aspect-square border-2 border-dashed border-gray-200 rounded-xl flex flex-col items-center justify-center cursor-pointer hover:bg-blue-50 hover:border-blue-200 transition-all group">
                            {uploading ? <Loader2 className="animate-spin text-blue-500" /> : <Upload className="text-gray-400 group-hover:text-blue-500 mb-2" />}
                            <span className="text-xs text-gray-500 group-hover:text-blue-600 font-medium">Add Image</span>
                            <input type="file" className="hidden" accept="image/*" onChange={handleUploadSingleImage} disabled={uploading} />
                        </label>

                        {/* Existing Images */}
                        {managingImagesFor.images?.map((img) => (
                            <div key={img.id} className="relative group aspect-square rounded-xl overflow-hidden border border-gray-100 shadow-sm">
                                <img src={img.image_url} className="w-full h-full object-cover" />
                                {img.is_primary && <div className="absolute top-2 left-2 bg-black/60 text-white text-[10px] px-2 py-0.5 rounded-full backdrop-blur-sm">Primary</div>}
                                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center gap-2">
                                    <button onClick={() => handleDeleteImage(img.id)} className="bg-white text-red-500 p-2 rounded-full hover:bg-red-50 transition-colors shadow-lg"><Trash2 size={16} /></button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
          </div>
      )}
    </div>
  );
}