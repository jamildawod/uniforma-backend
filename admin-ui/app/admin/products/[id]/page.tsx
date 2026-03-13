import { notFound } from "next/navigation";

import { ProductEditor } from "@/components/admin/product-editor";
import { ImageManager } from "@/components/admin/image-manager";
import { OverrideDiff } from "@/components/admin/override-diff";
import { OverrideEditor } from "@/components/admin/override-editor";
import { VariantList } from "@/components/admin/variant-list";
import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import { fetchAdminProduct } from "@/lib/api/server";

export default async function AdminProductDetailPage({
  params
}: {
  params: { id: string };
}) {
  const product = await fetchAdminProduct(params.id);
  if (!product) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <Panel>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">{product.external_id}</p>
            <h2 className="mt-2 text-2xl font-semibold text-ink">{product.name}</h2>
            <p className="mt-2 text-sm text-slate-600">{product.description ?? "No description available."}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant={product.is_active ? "success" : "danger"}>{product.is_active ? "Active" : "Inactive"}</Badge>
            {product.deleted_at ? <Badge variant="danger">Deleted</Badge> : null}
            {Object.keys(product.applied_overrides ?? {}).length > 0 ? <Badge variant="warning">Overrides applied</Badge> : null}
          </div>
        </div>
        <div className="mt-6 grid gap-3 text-sm text-slate-600 md:grid-cols-3">
          <p>Brand: {product.brand ?? "N/A"}</p>
          <p>Category: {product.category?.name ?? "Unassigned"}</p>
          <p>Last seen: {product.last_seen_at ? new Date(product.last_seen_at).toLocaleString() : "Unknown"}</p>
        </div>
      </Panel>

      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Product Management</p>
          <div className="mt-4">
            <ProductEditor mode="edit" product={product} />
          </div>
        </Panel>
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">PIM Source</p>
          <div className="mt-4 grid gap-3 text-sm text-slate-700">
            <p><span className="font-medium">Name:</span> {product.source_product?.name ?? product.name}</p>
            <p><span className="font-medium">Brand:</span> {product.source_product?.brand ?? product.brand ?? "N/A"}</p>
            <p><span className="font-medium">Description:</span> {product.source_product?.description ?? product.description ?? "N/A"}</p>
          </div>
        </Panel>
      </div>

      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Override Editor</p>
        <div className="mt-4">
          <OverrideEditor product={product} />
        </div>
      </Panel>

      <OverrideDiff product={product} />

      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Variants</p>
        <div className="mt-4">
          <VariantList variants={product.variants} />
        </div>
      </Panel>

      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Image Management</p>
        <div className="mt-4">
          <ImageManager images={product.images} productId={product.id} />
        </div>
      </Panel>

      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Sync Metadata</p>
        <div className="mt-4 grid gap-3 text-sm text-slate-600 md:grid-cols-2">
          <p>Created: {new Date(product.created_at).toLocaleString()}</p>
          <p>Updated: {new Date(product.updated_at).toLocaleString()}</p>
          <p>Deleted at: {product.deleted_at ? new Date(product.deleted_at).toLocaleString() : "Not deleted"}</p>
          <p>Last seen: {product.last_seen_at ? new Date(product.last_seen_at).toLocaleString() : "Unknown"}</p>
        </div>
      </Panel>
    </div>
  );
}
