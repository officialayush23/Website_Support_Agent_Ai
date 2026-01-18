import React, { useState } from "react";
import { Modal } from "antd";
import { toast } from "sonner";
import { apiRequest } from "../../../lib/api";
import { supabase } from "../../../lib/supabase";
import {
  Upload,
  Trash2,
  Star,
  Loader2,
  X,
} from "lucide-react";

export default function VariantImageManager({
  variant,
  open,
  onClose,
  onRefresh,
}) {
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  if (!variant) return null;

  /* ---------------- UPLOAD ---------------- */

  const uploadImage = async (file, isPrimary = false) => {
    setUploading(true);
    const t = toast.loading("Uploading image…");

    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;

      const form = new FormData();
      form.append("file", file);

      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/admin/products/images/?variant_id=${variant.id}&is_primary=${isPrimary}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: form,
        }
      );

      if (!res.ok) throw new Error();

      toast.success("Image uploaded", { id: t });
      onRefresh();
    } catch {
      toast.error("Upload failed", { id: t });
    } finally {
      setUploading(false);
    }
  };

  /* ---------------- DELETE ---------------- */

  const deleteImage = async (imageId) => {
    setDeletingId(imageId);
    try {
      await apiRequest(`/admin/products/images/${imageId}`, {
        method: "DELETE",
      });
      toast.success("Image removed");
      onRefresh();
    } catch {
      toast.error("Delete failed");
    } finally {
      setDeletingId(null);
    }
  };

  /* ---------------- UI ---------------- */

  return (
    <Modal
      open={open}
      onCancel={onClose}
      footer={null}
      width={720}
      title={`Images · ${variant.sku}`}
    >
      <div className="space-y-6">

        {/* Upload */}
        <label className="border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer hover:bg-gray-50 transition">
          {uploading ? (
            <Loader2 className="animate-spin text-gray-400" />
          ) : (
            <>
              <Upload className="text-gray-400 mb-2" />
              <span className="text-sm text-gray-600">
                Upload image
              </span>
            </>
          )}
          <input
            type="file"
            accept="image/*"
            hidden
            disabled={uploading}
            onChange={(e) =>
              uploadImage(
                e.target.files[0],
                variant.images?.length === 0
              )
            }
          />
        </label>

        {/* Images Grid */}
        <div className="grid grid-cols-3 sm:grid-cols-4 gap-4">
          {variant.images?.map((img) => (
            <div
              key={img.id}
              className="relative group aspect-square border rounded-xl overflow-hidden"
            >
              <img
                src={img.url}
                className="w-full h-full object-cover"
              />

              {img.is_primary && (
                <span className="absolute top-2 left-2 bg-black text-white text-[10px] px-2 py-0.5 rounded-full">
                  Primary
                </span>
              )}

              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-2">
                <button
                  onClick={() => deleteImage(img.id)}
                  className="bg-white p-2 rounded-full text-red-600"
                >
                  {deletingId === img.id ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Trash2 size={16} />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>

        {variant.images?.length === 0 && (
          <div className="text-sm text-gray-500 text-center">
            No images yet
          </div>
        )}
      </div>
    </Modal>
  );
}
