import React, { useEffect, useState } from "react";
import { Drawer, Steps } from "antd";
import { apiRequest } from "../../../lib/api";
import { supabase } from "../../../lib/supabase";
import { toast } from "sonner";
import {
  Plus,
  Loader2,
  Upload,
  X,
  Image as ImageIcon,
} from "lucide-react";

const { Step } = Steps;

export default function ProductCreateDrawer({ open, onClose, onSuccess }) {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);

  const [productId, setProductId] = useState(null);
  const [product, setProduct] = useState({
    name: "",
    category: "",
    description: "",
  });

  const [attributes, setAttributes] = useState([]);
  const [variants, setVariants] = useState([]);
  const [activeVariant, setActiveVariant] = useState(null);

  /* ---------------- LOAD ATTRIBUTE DEFINITIONS ---------------- */

  useEffect(() => {
    apiRequest("/admin/attributes")
      .then(setAttributes)
      .catch(() => toast.error("Failed to load attributes"));
  }, []);

  /* ---------------- STEP 1: CREATE PRODUCT ---------------- */

  const createProduct = async () => {
    if (!product.name || !product.category) {
      toast.error("Name and category required");
      return;
    }

    setLoading(true);
    const t = toast.loading("Creating product…");

    try {
      const res = await apiRequest("/admin/products", {
        method: "POST",
        body: JSON.stringify(product),
      });

      setProductId(res.id);
      setStep(1);
      toast.success("Product created", { id: t });
    } catch (e) {
      toast.error("Product creation failed", { id: t });
    } finally {
      setLoading(false);
    }
  };

  /* ---------------- STEP 2: CREATE VARIANT ---------------- */

  const createVariant = async () => {
    if (!activeVariant?.sku || !activeVariant?.price) {
      toast.error("SKU & price required");
      return;
    }

    setLoading(true);
    const t = toast.loading("Creating variant…");

    try {
      const v = await apiRequest("/products/admin/variants", {
        method: "POST",
        body: JSON.stringify({
          product_id: productId,
          sku: activeVariant.sku,
          price: parseFloat(activeVariant.price),
          attributes: activeVariant.attributes || {},
        }),
      });

      setVariants((prev) => [...prev, v]);
      setActiveVariant(null);
      toast.success("Variant added", { id: t });
    } catch {
      toast.error("Variant creation failed", { id: t });
    } finally {
      setLoading(false);
    }
  };

  /* ---------------- STEP 3: IMAGE UPLOAD ---------------- */

  const uploadVariantImage = async (variantId, file, isPrimary) => {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;

    const form = new FormData();
    form.append("file", file);

    await fetch(
      `${import.meta.env.VITE_API_URL}/admin/products/images?variant_id=${variantId}&is_primary=${isPrimary}`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      }
    );
  };

  /* ---------------- RESET ---------------- */

  const finish = () => {
    toast.success("Product fully created");
    onClose();
    onSuccess?.();
  };

  /* ======================================================== */

  return (
    <Drawer
      open={open}
      onClose={onClose}
      width={520}
      destroyOnClose
      title="Create Product"
    >
      <Steps current={step} size="small" className="mb-6">
        <Step title="Product" />
        <Step title="Variants" />
        <Step title="Images" />
      </Steps>

      {/* ---------------- STEP 1 ---------------- */}
      {step === 0 && (
        <div className="space-y-4">
          <input
            placeholder="Product name"
            className="w-full border rounded-lg px-3 py-2"
            value={product.name}
            onChange={(e) =>
              setProduct({ ...product, name: e.target.value })
            }
          />
          <input
            placeholder="Category"
            className="w-full border rounded-lg px-3 py-2"
            value={product.category}
            onChange={(e) =>
              setProduct({ ...product, category: e.target.value })
            }
          />
          <textarea
            placeholder="Description"
            className="w-full border rounded-lg px-3 py-2"
            rows={3}
            value={product.description}
            onChange={(e) =>
              setProduct({ ...product, description: e.target.value })
            }
          />

          <button
            onClick={createProduct}
            disabled={loading}
            className="w-full bg-black text-white py-2 rounded-lg flex justify-center gap-2"
          >
            {loading && <Loader2 className="animate-spin" size={16} />}
            Create Product
          </button>
        </div>
      )}

      {/* ---------------- STEP 2 ---------------- */}
      {step === 1 && (
        <div className="space-y-4">
          <div className="text-sm text-gray-500">
            Add variants (SKU + price + attributes)
          </div>

          <input
            placeholder="SKU"
            className="w-full border rounded-lg px-3 py-2"
            value={activeVariant?.sku || ""}
            onChange={(e) =>
              setActiveVariant((v) => ({ ...v, sku: e.target.value }))
            }
          />

          <input
            type="number"
            placeholder="Price"
            className="w-full border rounded-lg px-3 py-2"
            value={activeVariant?.price || ""}
            onChange={(e) =>
              setActiveVariant((v) => ({ ...v, price: e.target.value }))
            }
          />

          {/* Attributes */}
          {attributes.map((a) => (
            <input
              key={a.id}
              placeholder={a.name}
              className="w-full border rounded-lg px-3 py-2"
              onChange={(e) =>
                setActiveVariant((v) => ({
                  ...v,
                  attributes: {
                    ...(v?.attributes || {}),
                    [a.name]: e.target.value,
                  },
                }))
              }
            />
          ))}

          <button
            onClick={createVariant}
            disabled={loading}
            className="w-full bg-gray-900 text-white py-2 rounded-lg flex justify-center gap-2"
          >
            {loading && <Loader2 className="animate-spin" size={16} />}
            Add Variant
          </button>

          {variants.length > 0 && (
            <button
              onClick={() => setStep(2)}
              className="w-full border py-2 rounded-lg"
            >
              Continue to Images →
            </button>
          )}
        </div>
      )}

      {/* ---------------- STEP 3 ---------------- */}
      {step === 2 && (
        <div className="space-y-4">
          {variants.map((v) => (
            <label
              key={v.id}
              className="border rounded-xl p-4 flex items-center gap-3 cursor-pointer"
            >
              <ImageIcon />
              <span className="flex-1 text-sm">{v.sku}</span>
              <input
                type="file"
                hidden
                accept="image/*"
                onChange={(e) =>
                  uploadVariantImage(v.id, e.target.files[0], true)
                }
              />
            </label>
          ))}

          <button
            onClick={finish}
            className="w-full bg-black text-white py-2 rounded-lg"
          >
            Finish
          </button>
        </div>
      )}
    </Drawer>
  );
}
