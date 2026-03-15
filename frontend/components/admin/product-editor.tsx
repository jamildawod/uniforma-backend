"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import {
  useCreateAdminProduct,
  useCreateProductVariant,
  useDeleteAdminProduct,
  usePublishAdminProduct,
  useUpdateAdminProduct,
  useUploadAdminImage
} from "@/hooks/use-product-mutations";
import type {
  AdminAttributeValuePayload,
  AdminProduct,
  AdminProductUpsertPayload,
  AdminVariantPayload,
  AttributeDefinition,
  Brand,
  Category,
  ProductStatus
} from "@/lib/types/products";

type ProductEditorProps = {
  mode: "create" | "edit";
  product?: AdminProduct;
  brands: Brand[];
  categories: Category[];
  attributes: AttributeDefinition[];
};

function toInitialState(product?: AdminProduct): AdminProductUpsertPayload {
  return {
    name: product?.name ?? "",
    slug: product?.slug ?? "",
    description: product?.description ?? "",
    brand_id: product?.brand_id ?? null,
    category_id: product?.category_id ?? null,
    status: product?.status ?? "draft",
    image_url: product?.image_url ?? "",
    is_active: product?.is_active ?? true,
    variants: [],
    attributes:
      product?.attributes.map((item) => ({
        attribute_id: item.attribute_id,
        value: item.value
      })) ?? []
  };
}

const statusOptions: ProductStatus[] = ["draft", "active", "archived"];

export function ProductEditor({ mode, product, brands, categories, attributes }: ProductEditorProps) {
  const router = useRouter();
  const [form, setForm] = useState<AdminProductUpsertPayload>(toInitialState(product));
  const [newVariant, setNewVariant] = useState<AdminVariantPayload>({
    sku: "",
    ean: "",
    size: "",
    color: "",
    price: "",
    stock_quantity: 0,
    is_active: true
  });
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const createMutation = useCreateAdminProduct();
  const updateMutation = useUpdateAdminProduct(product?.id ?? "");
  const variantMutation = useCreateProductVariant(product?.id ?? "");
  const deleteMutation = useDeleteAdminProduct(product?.id ?? "");
  const publishMutation = usePublishAdminProduct(product?.id ?? "");
  const uploadMutation = useUploadAdminImage();

  const saveMutation = mode === "create" ? createMutation : updateMutation;

  function setAttributeValue(attributeId: number, value: string) {
    setForm((current) => {
      const next = current.attributes.filter((item) => item.attribute_id !== attributeId);
      if (value.trim()) {
        next.push({ attribute_id: attributeId, value });
      }
      return { ...current, attributes: next };
    });
  }

  function getAttributeValue(attributeId: number): string {
    return form.attributes.find((item) => item.attribute_id === attributeId)?.value ?? "";
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    try {
      const saved = await saveMutation.mutateAsync({
        ...form,
        slug: form.slug?.trim() || null,
        description: form.description?.trim() || null,
        brand_id: form.brand_id ?? null,
        category_id: form.category_id ?? null,
        image_url: form.image_url?.trim() || null,
        variants: mode === "create" ? form.variants ?? [] : [],
        attributes: form.attributes.filter((item) => item.value.trim())
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
      setForm((current) => ({
        ...current,
        is_active: updated.is_active,
        status: updated.status
      }));
      setMessage(nextState ? "Product published." : "Product unpublished.");
      startTransition(() => router.refresh());
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to update publication status.");
    }
  }

  async function handleVariantCreate() {
    if (!product || !newVariant.sku.trim()) return;
    setMessage(null);
    try {
      await variantMutation.mutateAsync({
        ...newVariant,
        ean: newVariant.ean?.trim() || null,
        size: newVariant.size?.trim() || null,
        color: newVariant.color?.trim() || null,
        price: newVariant.price?.trim() || null
      });
      setNewVariant({
        sku: "",
        ean: "",
        size: "",
        color: "",
        price: "",
        stock_quantity: 0,
        is_active: true
      });
      setMessage("Variant added.");
      startTransition(() => router.refresh());
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to add variant.");
    }
  }

  const saving = saveMutation.isPending || isPending;

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
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
            value={form.slug ?? ""}
          />
        </label>
        <label className="space-y-2 text-sm text-slate-700">
          <span className="font-medium">Brand</span>
          <select
            className="w-full rounded-2xl border border-slate-200 px-4 py-3"
            onChange={(event) => setForm((current) => ({ ...current, brand_id: event.target.value ? Number(event.target.value) : null }))}
            value={form.brand_id ?? ""}
          >
            <option value="">Select brand</option>
            {brands.map((brand) => (
              <option key={brand.id} value={brand.id}>
                {brand.name}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-2 text-sm text-slate-700">
          <span className="font-medium">Category</span>
          <select
            className="w-full rounded-2xl border border-slate-200 px-4 py-3"
            onChange={(event) => setForm((current) => ({ ...current, category_id: event.target.value ? Number(event.target.value) : null }))}
            value={form.category_id ?? ""}
          >
            <option value="">Select category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm text-slate-700">
          <span className="font-medium">Status</span>
          <select
            className="w-full rounded-2xl border border-slate-200 px-4 py-3"
            onChange={(event) => setForm((current) => ({ ...current, status: event.target.value as ProductStatus }))}
            value={form.status}
          >
            {statusOptions.map((statusValue) => (
              <option key={statusValue} value={statusValue}>
                {statusValue}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-3 pt-8 text-sm text-slate-700">
          <input
            checked={form.is_active}
            onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.checked }))}
            type="checkbox"
          />
          Publicly visible
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
          <span className="font-medium">Primary image</span>
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

      {attributes.length > 0 ? (
        <div className="space-y-4 rounded-3xl border border-slate-200 p-5">
          <p className="text-sm font-semibold text-ink">Attributes</p>
          <div className="grid gap-4 md:grid-cols-2">
            {attributes.map((attribute) => (
              <label key={attribute.id} className="space-y-2 text-sm text-slate-700">
                <span className="font-medium">{attribute.name}</span>
                <input
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3"
                  onChange={(event) => setAttributeValue(attribute.id, event.target.value)}
                  value={getAttributeValue(attribute.id)}
                />
              </label>
            ))}
          </div>
        </div>
      ) : null}

      {mode === "create" ? (
        <div className="space-y-4 rounded-3xl border border-slate-200 p-5">
          <p className="text-sm font-semibold text-ink">Variants to create</p>
          <div className="grid gap-3 md:grid-cols-3">
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="SKU" value={newVariant.sku} onChange={(event) => setNewVariant((current) => ({ ...current, sku: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="EAN" value={newVariant.ean ?? ""} onChange={(event) => setNewVariant((current) => ({ ...current, ean: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Size" value={newVariant.size ?? ""} onChange={(event) => setNewVariant((current) => ({ ...current, size: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Color" value={newVariant.color ?? ""} onChange={(event) => setNewVariant((current) => ({ ...current, color: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Price" value={newVariant.price ?? ""} onChange={(event) => setNewVariant((current) => ({ ...current, price: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Stock" type="number" value={newVariant.stock_quantity} onChange={(event) => setNewVariant((current) => ({ ...current, stock_quantity: Number(event.target.value) }))} />
          </div>
          <button
            className="rounded-2xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
            onClick={() =>
              setForm((current) => ({
                ...current,
                variants: [...(current.variants ?? []), newVariant]
              }))
            }
            type="button"
          >
            Add variant to payload
          </button>
          <div className="space-y-2 text-sm text-slate-600">
            {(form.variants ?? []).map((variant, index) => (
              <p key={`${variant.sku}-${index}`}>{variant.sku} · {variant.color || "-"} · {variant.size || "-"}</p>
            ))}
          </div>
        </div>
      ) : null}

      {mode === "edit" ? (
        <div className="space-y-4 rounded-3xl border border-slate-200 p-5">
          <p className="text-sm font-semibold text-ink">Add variant</p>
          <div className="grid gap-3 md:grid-cols-3">
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="SKU" value={newVariant.sku} onChange={(event) => setNewVariant((current) => ({ ...current, sku: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="EAN" value={newVariant.ean ?? ""} onChange={(event) => setNewVariant((current) => ({ ...current, ean: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Size" value={newVariant.size ?? ""} onChange={(event) => setNewVariant((current) => ({ ...current, size: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Color" value={newVariant.color ?? ""} onChange={(event) => setNewVariant((current) => ({ ...current, color: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Price" value={newVariant.price ?? ""} onChange={(event) => setNewVariant((current) => ({ ...current, price: event.target.value }))} />
            <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Stock" type="number" value={newVariant.stock_quantity} onChange={(event) => setNewVariant((current) => ({ ...current, stock_quantity: Number(event.target.value) }))} />
          </div>
          <button
            className="rounded-2xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
            disabled={variantMutation.isPending}
            onClick={() => void handleVariantCreate()}
            type="button"
          >
            {variantMutation.isPending ? "Adding..." : "Add variant"}
          </button>
        </div>
      ) : null}

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
