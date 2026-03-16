import { Panel } from "@/components/ui/panel";
import type { AdminAnalytics } from "@/types/intelligence";

export function AnalyticsOverview({ analytics }: { analytics: AdminAnalytics }) {
  const max = Math.max(...analytics.products_per_category.map((item) => item.total_products), 1);

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Total products</p>
          <p className="mt-3 text-4xl font-semibold text-ink">{analytics.total_products}</p>
        </Panel>
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Categories</p>
          <p className="mt-3 text-4xl font-semibold text-ink">{analytics.products_per_category.length}</p>
        </Panel>
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Last supplier sync</p>
          <p className="mt-3 text-lg font-semibold text-ink">{analytics.last_supplier_sync ? new Date(analytics.last_supplier_sync).toLocaleString() : "No sync yet"}</p>
        </Panel>
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Images stored</p>
          <p className="mt-3 text-4xl font-semibold text-ink">{analytics.total_images_stored}</p>
        </Panel>
      </div>

      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Products per category</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Catalog distribution</h2>
        <div className="mt-6 space-y-4">
          {analytics.products_per_category.map((item) => (
            <div key={item.category}>
              <div className="mb-2 flex items-center justify-between gap-4 text-sm">
                <span className="font-medium text-ink">{item.category}</span>
                <span className="text-slate-500">{item.total_products}</span>
              </div>
              <div className="h-3 rounded-full bg-slate-100">
                <div className="h-3 rounded-full bg-[#10233f]" style={{ width: `${Math.max((item.total_products / max) * 100, 6)}%` }} />
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
