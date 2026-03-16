import Link from "next/link";

import { Panel } from "@/components/ui/panel";
import { fetchAdminProducts, fetchAdminQuotes, fetchSystemHealthSummary, fetchSyncRuns } from "@/lib/api/server";

export default async function AdminDashboardPage() {
  const [products, quotes, summary, syncRuns] = await Promise.all([
    fetchAdminProducts({ page: 1, pageSize: 200, isActive: "all", deleted: "all", hasOverride: "all" }),
    fetchAdminQuotes(),
    fetchSystemHealthSummary(),
    fetchSyncRuns()
  ]);

  const latestSync = syncRuns[0];

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Products count</p>
          <p className="mt-3 text-4xl font-semibold text-ink">{summary?.total_products ?? products.length}</p>
        </Panel>
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Quote requests</p>
          <p className="mt-3 text-4xl font-semibold text-ink">{quotes.length}</p>
        </Panel>
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Last sync</p>
          <p className="mt-3 text-lg font-semibold text-ink">
            {summary?.last_successful_sync_at ? new Date(summary.last_successful_sync_at).toLocaleString() : "No sync yet"}
          </p>
        </Panel>
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">System health</p>
          <p className="mt-3 text-2xl font-semibold capitalize text-ink">{summary?.status ?? "unavailable"}</p>
        </Panel>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel>
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Recent quotes</p>
              <h2 className="mt-1 text-2xl font-semibold text-ink">Customer pipeline</h2>
            </div>
            <Link className="text-sm font-medium text-clay" href="/admin/quotes">
              View all
            </Link>
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
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Operations</p>
          <div className="mt-6 space-y-4 text-sm text-slate-600">
            <p>Active products: {summary?.active_products ?? products.filter((product) => product.is_active).length}</p>
            <p>Deleted products: {summary?.deleted_products ?? products.filter((product) => product.deleted_at).length}</p>
            <p>Running syncs: {summary?.running_syncs ?? 0}</p>
            <p>Latest run status: {latestSync?.status ?? "n/a"}</p>
          </div>
        </Panel>
      </div>
    </div>
  );
}
