import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import type { AdminProduct, ProductListFilters } from "@/lib/types/products";

function getSyncVariant(product: AdminProduct): "success" | "warning" | "danger" {
  if (product.deleted_at) return "danger";
  if (Object.keys(product.applied_overrides ?? {}).length > 0) return "warning";
  return "success";
}

function getSyncLabel(product: AdminProduct): string {
  if (product.deleted_at) return "Deleted";
  if (Object.keys(product.applied_overrides ?? {}).length > 0) return "Override";
  return "Synced";
}

export function ProductTable({
  products,
  filters
}: {
  products: AdminProduct[];
  filters: ProductListFilters;
}) {
  if (products.length === 0) {
    return <EmptyState description="Adjust filters or trigger a sync run." title="No products found" />;
  }

  return (
    <div className="overflow-hidden rounded-3xl bg-white shadow-panel">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Product</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Variants</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">State</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Sync</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Updated</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {products.map((product) => (
            <tr key={product.id} className="hover:bg-slate-50/80">
              <td className="px-4 py-4">
                <Link className="font-semibold text-ink" href={`/admin/products/${product.id}`}>
                  {product.name}
                </Link>
                <p className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-500">{product.external_id}</p>
              </td>
              <td className="px-4 py-4 text-slate-600">
                <p>{product.variants.length} variants</p>
                <p className="text-xs text-slate-400">{product.variants[0]?.sku ?? "No SKU"}</p>
              </td>
              <td className="px-4 py-4">
                <div className="flex gap-2">
                  <Badge variant={product.is_active ? "success" : "danger"}>{product.is_active ? "Active" : "Inactive"}</Badge>
                  {Object.keys(product.applied_overrides ?? {}).length > 0 ? <Badge variant="warning">Override</Badge> : null}
                </div>
              </td>
              <td className="px-4 py-4">
                <Badge variant={getSyncVariant(product)}>{getSyncLabel(product)}</Badge>
              </td>
              <td className="px-4 py-4 text-slate-500">{new Date(product.updated_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-sm text-slate-500">
        <span>Page {filters.page}</span>
        <div className="flex gap-2">
          {filters.page > 1 ? <Link href={buildProductPageHref(filters, filters.page - 1)}>Previous</Link> : <span className="opacity-40">Previous</span>}
          <Link href={buildProductPageHref(filters, filters.page + 1)}>Next</Link>
        </div>
      </div>
    </div>
  );
}

function buildProductPageHref(filters: ProductListFilters, page: number): string {
  const params = new URLSearchParams({
    page: String(page)
  });

  if (filters.search) {
    params.set("search", filters.search);
  }
  if (filters.filter) {
    params.set("filter", filters.filter);
  }
  if (filters.isActive && filters.isActive !== "all") {
    params.set("isActive", filters.isActive);
  }
  if (filters.deleted && filters.deleted !== "all") {
    params.set("deleted", filters.deleted);
  }
  if (filters.hasOverride && filters.hasOverride !== "all") {
    params.set("hasOverride", filters.hasOverride);
  }

  return `/admin/products?${params.toString()}`;
}
