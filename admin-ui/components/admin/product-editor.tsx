"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import {
  useCreateAdminProduct,
  useDeleteAdminProduct,
  usePublishAdminProduct,
  useUpdateAdminProduct,
  useUploadAdminImage
} from "@/hooks/use-product-mutations";
import type { AdminProduct, AdminProductUpsertPayload } from "@/lib/types/products";

type ProductEditorProps = {
  mode: "create" | "edit";
  product?: AdminProduct;
};

function toInitialState(product?: AdminProduct): AdminProductUpsertPayload {
  return {
    name: product?.name ?? "",
    slug: product?.slug ?? "",
    description: product?.description ?? "",
    brand: product?.brand ?? "",
    category: product?.category?.name ?? "",
    image_url: product?.image_url ?? "",
    is_active: product?.is_active ?? true
  };
}

export function ProductEditor({ mode, product }: ProductEditorProps) {
  const router = useRouter();
  const [form, setForm] = useState<AdminProductUpsertPayload>(toInitialState(product));
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const createMutation = useCreateAdminProduct();
  const updateMutation = useUpdateAdminProduct(product?.id ?? "");
  const deleteMutation = useDeleteAdminProduct(product?.id ?? "");
  const publishMutation = usePublishAdminProduct(product?.id ?? "");
  const uploadMutation = useUploadAdminImage();

  const saveMutation = mode === "create" ? createMutation : updateMutation;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    try {
      const saved = await saveMutation.mutateAsync({
        ...form,
        slug: form.slug?.trim() || null,
        description: form.description?.trim() || null,
        brand: form.brand?.trim() || null,
        category: form.category?.trim() || null,
        image_url: form.image_url?.trim() || null
      });
      setMessage(mode === "create" ? "Product created." : "Product updated.");
      startTransition(() => {
        router.push(`/admin/products/${saved.id}`);
        router.refresh();
      });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to save product.");
    }
  }

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setMessage(null);
    try {
      const uploaded = await uploadMutation.mutateAsync(file);
      setForm((current) => ({ ...current, image_url: uploaded.url }));
      setMessage("Image uploaded.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Upload failed.");
    } finally {
      event.target.value = "";
    }
  }

  async function handleDelete() {
    if (!product) return;
    setMessage(null);
    try {
      await deleteMutation.mutateAsync();
      startTransition(() => {
        router.push("/admin/products");
        router.refresh();
      });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Delete failed.");
    }
  }

  async function handlePublication(nextState: boolean) {
    if (!product) return;
    setMessage(null);
    try {
      const updated = await publishMutation.mutateAsync(nextState);
      setForm((current) => ({ ...current, is_active: updated.is_active }));
      setMessage(nextState ? "Product published." : "Product unpublished.");
      startTransition(() => router.refresh());
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to update publication status.");
    }
  }

  const saving = saveMutation.isPending || isPending;

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm text-slate-700">
          <span className="font-medium">Name</span>
          <input
            className="w-full rounded-2xl border border-slate-200 px-4 py-3"
            onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
            required
            value={form.name}
          />
        </label>
        <label className="space-y-2 text-sm text-slate-700">
          <span className="font-medium">Slug</span>
          <input
            className="w-full rounded-2xl border border-slate-200 px-4 py-3"
            onChange={(event) => setForm((current) => ({ ...current, slug: event.target.value }))}
            placeholder="auto-generated if empty"
            value={form.slug ?? ""}
          />
        </label>
        <label className="space-y-2 text-sm text-slate-700">
          <span className="font-medium">Brand</span>
          <input
            className="w-full rounded-2xl border border-slate-200 px-4 py-3"
            onChange={(event) => setForm((current) => ({ ...current, brand: event.target.value }))}
            value={form.brand ?? ""}
          />
        </label>
        <label className="space-y-2 text-sm text-slate-700">
          <span className="font-medium">Category</span>
          <input
            className="w-full rounded-2xl border border-slate-200 px-4 py-3"
            onChange={(event) => setForm((current) => ({ ...current, category: event.target.value }))}
            value={form.category ?? ""}
          />
        </label>
      </div>

      <label className="block space-y-2 text-sm text-slate-700">
        <span className="font-medium">Description</span>
        <textarea
          className="min-h-36 w-full rounded-2xl border border-slate-200 px-4 py-3"
          onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
          value={form.description ?? ""}
        />
      </label>

      <div className="grid gap-4 md:grid-cols-[1fr_auto] md:items-end">
        <label className="space-y-2 text-sm text-slate-700">
          <span className="font-medium">Image URL</span>
          <input
            className="w-full rounded-2xl border border-slate-200 px-4 py-3"
            onChange={(event) => setForm((current) => ({ ...current, image_url: event.target.value }))}
            placeholder="/uploads/example.jpg or external URL"
            value={form.image_url ?? ""}
          />
        </label>
        <label className="inline-flex cursor-pointer items-center justify-center rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700">
          <input accept="image/*" className="hidden" onChange={handleUpload} type="file" />
          {uploadMutation.isPending ? "Uploading..." : "Upload image"}
        </label>
      </div>

      {form.image_url ? (
        <div className="overflow-hidden rounded-3xl border border-slate-200 bg-slate-50">
          <img alt={form.name || "Product preview"} className="h-56 w-full object-cover" src={form.image_url} />
        </div>
      ) : null}

      <label className="flex items-center gap-3 text-sm text-slate-700">
        <input
          checked={form.is_active}
          onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.checked }))}
          type="checkbox"
        />
        Published on public site
      </label>

      <div className="flex flex-wrap gap-3">
        <button className="rounded-2xl bg-ink px-5 py-3 text-sm font-semibold text-white" disabled={saving} type="submit">
          {saving ? "Saving..." : mode === "create" ? "Create product" : "Save changes"}
        </button>
        {product ? (
          <button
            className="rounded-2xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700"
            disabled={publishMutation.isPending}
            onClick={() => void handlePublication(!form.is_active)}
            type="button"
          >
            {form.is_active ? "Unpublish" : "Publish"}
          </button>
        ) : null}
        {product ? (
          <button
            className="rounded-2xl border border-red-300 px-5 py-3 text-sm font-semibold text-red-700"
            disabled={deleteMutation.isPending}
            onClick={() => void handleDelete()}
            type="button"
          >
            Delete product
          </button>
        ) : null}
      </div>

      {message ? <p className="text-sm text-slate-600">{message}</p> : null}
    </form>
  );
}
