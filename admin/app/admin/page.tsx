import Link from "next/link";

import { AnalyticsOverview } from "@/components/admin/analytics-overview";
import { Panel } from "@/components/ui/panel";
import { fetchAdminAnalytics, fetchAdminQuotes, fetchSupplierSyncOverview } from "@/lib/api/server";

export default async function AdminDashboardPage() {
  const [analytics, quotes, supplierSync] = await Promise.all([
    fetchAdminAnalytics(),
    fetchAdminQuotes(),
    fetchSupplierSyncOverview(),
  ]);

  return (
    <div className="space-y-6">
      <Panel>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Dashboard</p>
            <h2 className="mt-1 text-2xl font-semibold text-ink">Operations snapshot</h2>
            <p className="mt-2 text-sm text-slate-600">Overview of product volume, supplier sync state, and inbound quote activity.</p>
          </div>
          <div className="flex gap-3">
            <Link className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white" href="/admin/products">Manage products</Link>
            <Link className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium" href="/admin/integrations/sync-monitor">Open sync monitor</Link>
          </div>
        </div>
      </Panel>

      {analytics ? <AnalyticsOverview analytics={analytics} /> : null}

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel>
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Recent quotes</p>
              <h2 className="mt-1 text-2xl font-semibold text-ink">Customer pipeline</h2>
            </div>
            <Link className="text-sm font-medium text-clay" href="/admin/quotes">View all</Link>
          </div>
          <div className="mt-6 space-y-4">
            {quotes.slice(0, 5).map((quote) => (
              <div key={quote.id} className="rounded-2xl border border-slate-200 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-medium text-ink">{quote.company || quote.name}</p>
                  <span className="text-xs uppercase tracking-[0.16em] text-slate-500">{quote.status}</span>
                </div>
                <p className="mt-2 text-sm text-slate-600">{quote.message}</p>
              </div>
            ))}
            {quotes.length === 0 ? <p className="text-sm text-slate-500">No quote requests yet.</p> : null}
          </div>
        </Panel>

        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Supplier sync</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">Hejco status</h2>
          <div className="mt-6 space-y-4 text-sm text-slate-600">
            <p>Last sync: {supplierSync?.last_sync_time ? new Date(supplierSync.last_sync_time).toLocaleString() : "Never"}</p>
            <p>Status: {supplierSync?.last_sync_status ?? "Unknown"}</p>
            <p>Products imported: {supplierSync?.products_imported ?? 0}</p>
            <p>Latest error: {supplierSync?.errors ?? "None"}</p>
          </div>
        </Panel>
      </div>
    </div>
  );
}
