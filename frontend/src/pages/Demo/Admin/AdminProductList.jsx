import React, { useEffect, useState } from "react";
import { apiRequest } from "../../../lib/api";
import { toast } from "sonner";
import {
  Plus,
  Trash2,
  Pencil,
  Power,
  Package,
  MoreHorizontal,
} from "lucide-react";
import { Popover } from "antd";
import ProductCreateDrawer from "./ProductCreateDrawer";
import VariantManager from "./VariantManager";

export default function AdminProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [activeProduct, setActiveProduct] = useState(null);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const data = await apiRequest("/products");
      setProducts(data);
    } catch {
      toast.error("Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleDelete = async (id) => {
    if (!confirm("Delete product permanently?")) return;
    try {
      await apiRequest(`/admin/products/${id}`, { method: "DELETE" });
      toast.success("Product deleted");
      fetchProducts();
    } catch {
      toast.error("Delete failed");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Products</h2>
          <p className="text-sm text-gray-500">
            Manage catalog and variants
          </p>
        </div>

        <button
          onClick={() => setShowCreate(true)}
          className="bg-black text-white px-4 py-2 rounded-xl flex items-center gap-2"
        >
          <Plus size={16} /> New Product
        </button>
      </div>

      {/* Product Cards */}
      {loading ? (
        <div className="text-gray-400">Loading…</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {products.map((p) => (
            <div
              key={p.id}
              className="bg-white border rounded-2xl p-4 shadow-sm hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center">
                    <Package size={18} />
                  </div>
                  <div>
                    <p className="font-semibold">{p.name}</p>
                    <p className="text-xs text-gray-500">{p.category}</p>
                  </div>
                </div>

                <Popover
                  trigger="click"
                  content={
                    <div className="flex flex-col gap-1">
                      <button
                        onClick={() => setActiveProduct(p)}
                        className="flex items-center gap-2 text-sm hover:bg-gray-100 px-2 py-1 rounded"
                      >
                        <Pencil size={14} /> Edit
                      </button>
                      <button
                        onClick={() => handleDelete(p.id)}
                        className="flex items-center gap-2 text-sm text-red-600 hover:bg-red-50 px-2 py-1 rounded"
                      >
                        <Trash2 size={14} /> Delete
                      </button>
                    </div>
                  }
                >
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <MoreHorizontal size={16} />
                  </button>
                </Popover>
              </div>

              {/* Variants */}
              <div className="mt-4">
                <button
                  onClick={() => setActiveProduct(p)}
                  className="text-sm text-blue-600 hover:underline"
                >
                  Manage variants →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Drawer */}
      {showCreate && (
        <ProductCreateDrawer
          open={showCreate}
          onClose={() => setShowCreate(false)}
          onSuccess={fetchProducts}
        />
      )}

      {/* Variant Manager */}
      {activeProduct && (
        <VariantManager
          product={activeProduct}
          onClose={() => setActiveProduct(null)}
        />
      )}
    </div>
  );
}
