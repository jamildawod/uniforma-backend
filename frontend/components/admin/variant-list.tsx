import { Badge } from "@/components/ui/badge";
import type { ProductVariant } from "@/lib/types/products";

export function VariantList({ variants }: { variants: ProductVariant[] }) {
  return (
    <div className="space-y-4">
      {variants.map((variant) => (
        <div key={variant.id} className="rounded-2xl border border-slate-200 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="font-semibold text-ink">{variant.sku}</p>
              <p className="text-sm text-slate-500">
                {variant.color ?? "No color"} / {variant.size ?? "No size"}
              </p>
            </div>
            <div className="flex gap-2">
              <Badge variant={variant.is_active ? "success" : "danger"}>{variant.is_active ? "Active" : "Inactive"}</Badge>
            </div>
          </div>
          <div className="mt-3 grid gap-3 text-sm text-slate-600 md:grid-cols-4">
            <p>EAN: {variant.ean ?? "N/A"}</p>
            <p>Price: {variant.price ? `${variant.price} SEK` : "N/A"}</p>
            <p>Stock: {variant.stock_quantity}</p>
            <p>Updated: {new Date(variant.updated_at).toLocaleString()}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
