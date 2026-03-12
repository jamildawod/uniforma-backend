import { Panel } from "@/components/ui/panel";
import type { AdminProduct } from "@/lib/types/products";

const OVERRIDE_FIELDS = ["name", "description", "brand"] as const;

export function OverrideDiff({ product }: { product: AdminProduct }) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {OVERRIDE_FIELDS.map((field) => {
        const sourceValue =
          product.source_product?.[field] ??
          (field === "name" ? product.name : field === "description" ? product.description : product.brand) ??
          null;
        const overrideValue = product.applied_overrides[field] ?? null;
        const finalValue = overrideValue ?? sourceValue;

        return (
          <Panel key={field}>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">{field}</p>
            <div className="mt-4 space-y-3 text-sm">
              <div>
                <p className="font-medium text-slate-500">PIM</p>
                <p className="mt-1 text-ink">{String(sourceValue ?? "—")}</p>
              </div>
              <div>
                <p className="font-medium text-slate-500">Override</p>
                <p className="mt-1 text-ink">{String(overrideValue ?? "—")}</p>
              </div>
              <div>
                <p className="font-medium text-slate-500">Final</p>
                <p className="mt-1 text-ink">{String(finalValue ?? "—")}</p>
              </div>
            </div>
          </Panel>
        );
      })}
    </div>
  );
}
