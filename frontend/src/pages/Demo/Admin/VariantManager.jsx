// frontend/src/pages/Demo/Admin/VariantManager.jsx

import React, { useEffect, useState } from "react";
import { Modal, Popconfirm } from "antd";
import { apiRequest } from "../../../lib/api";
import { toast } from "sonner";
import {
  Pencil,
  Trash2,
  Image as ImageIcon,
  Loader2,
  Plus,
} from "lucide-react";

export default function VariantManager({ productId, onClose }) {
  const [variants, setVariants] = useState([]);
  const [attributes, setAttributes] = useState([]);
  const [editing, setEditing] = useState(null);
  const [loading, setLoading] = useState(false);

  /* ---------------- LOAD DATA ---------------- */

  useEffect(() => {
    fetchVariants();
    fetchAttributes();
  }, []);

  const fetchVariants = async () => {
    try {
      const res = await apiRequest(`/products/${productId}/full`);
      setVariants(res.variants || []);
    } catch {
      toast.error("Failed to load variants");
    }
  };

  const fetchAttributes = async () => {
    try {
      setAttributes(await apiRequest("/admin/attributes"));
    } catch {
      toast.error("Failed to load attributes");
    }
  };

  /* ---------------- UPDATE VARIANT ---------------- */

  const saveVariant = async () => {
    setLoading(true);
    const t = toast.loading("Updating variant…");

    try {
      await apiRequest(`/admin/variants/${editing.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          sku: editing.sku,
          price: parseFloat(editing.price),
          attributes: editing.attributes,
        }),
      });

      toast.success("Variant updated", { id: t });
      setEditing(null);
      fetchVariants();
    } catch {
      toast.error("Update failed", { id: t });
    } finally {
      setLoading(false);
    }
  };

  /* ---------------- DELETE ---------------- */

  const deleteVariant = async (variantId) => {
    try {
      await apiRequest(`/admin/variants/${variantId}`, { method: "DELETE" });
      setVariants((v) => v.filter((x) => x.id !== variantId));
      toast.success("Variant deleted");
    } catch {
      toast.error("Delete failed");
    }
  };

  /* ================================================= */

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Variants</h2>
        <button
          onClick={onClose}
          className="text-sm text-gray-500 hover:text-black"
        >
          Close
        </button>
      </div>

      {variants.length === 0 && (
        <div className="text-gray-500 text-sm">
          No variants yet. Create one first.
        </div>
      )}

      <div className="space-y-3">
        {variants.map((v) => (
          <div
            key={v.id}
            className="border rounded-xl p-4 flex items-center justify-between hover:bg-gray-50"
          >
            <div>
              <div className="font-medium">{v.sku}</div>
              <div className="text-sm text-gray-500">
                ₹{v.price} · {Object.keys(v.attributes || {}).length} attributes
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setEditing(v)}
                className="p-2 border rounded-lg hover:bg-gray-100"
              >
                <Pencil size={16} />
              </button>

              <Popconfirm
                title="Delete this variant?"
                onConfirm={() => deleteVariant(v.id)}
              >
                <button className="p-2 border rounded-lg hover:bg-red-50 text-red-600">
                  <Trash2 size={16} />
                </button>
              </Popconfirm>
            </div>
          </div>
        ))}
      </div>

      {/* ---------------- EDIT MODAL ---------------- */}

      <Modal
        open={!!editing}
        onCancel={() => setEditing(null)}
        onOk={saveVariant}
        okText={loading ? "Saving…" : "Save"}
        confirmLoading={loading}
        title="Edit Variant"
      >
        {editing && (
          <div className="space-y-4">
            <input
              className="w-full border rounded-lg px-3 py-2"
              value={editing.sku}
              onChange={(e) =>
                setEditing({ ...editing, sku: e.target.value })
              }
            />

            <input
              type="number"
              className="w-full border rounded-lg px-3 py-2"
              value={editing.price}
              onChange={(e) =>
                setEditing({ ...editing, price: e.target.value })
              }
            />

            {attributes.map((a) => (
              <input
                key={a.id}
                placeholder={a.name}
                className="w-full border rounded-lg px-3 py-2"
                value={editing.attributes?.[a.name] || ""}
                onChange={(e) =>
                  setEditing({
                    ...editing,
                    attributes: {
                      ...editing.attributes,
                      [a.name]: e.target.value,
                    },
                  })
                }
              />
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
}
