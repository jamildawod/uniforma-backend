import { AnomalyTable } from "@/components/admin/intelligence/AnomalyTable";
import { MetricCard } from "@/components/admin/intelligence/MetricCard";
import { OverrideConflictTable } from "@/components/admin/intelligence/OverrideConflictTable";
import { SyncHealthPanel } from "@/components/admin/intelligence/SyncHealthPanel";
import { ErrorState } from "@/components/ui/error-state";
import { Panel } from "@/components/ui/panel";
import { fetchWithToken } from "@/lib/api/server";
import type { SystemHealth } from "@/types/intelligence";

export default async function IntelligencePage() {
  try {
    const summary = await fetchWithToken<SystemHealth>("/api/v1/admin/intelligence/summary");

    return (
      <div className="space-y-6">
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Diagnostics</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">Admin Intelligence</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-600">
            PIM sync visibility, catalog data quality, and override conflict detection. Summary metrics are server-rendered; diagnostic tables stream through React Query for interactive refresh and pagination.
          </p>
        </Panel>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard detail="All catalog entities currently tracked." severity={summary.status} title="Total Products" value={summary.total_products} />
          <MetricCard detail="Products currently visible to downstream channels." severity="healthy" title="Active Products" value={summary.active_products} />
          <MetricCard detail="Soft-deleted records awaiting review." severity={summary.deleted_products > 0 ? "warning" : "healthy"} title="Deleted Products" value={summary.deleted_products} />
          <MetricCard detail="Concurrent sync workers currently active." severity={summary.running_syncs > 0 ? "warning" : "healthy"} title="Running Syncs" value={summary.running_syncs} />
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <AnomalyTable />
          <SyncHealthPanel />
        </section>

        <OverrideConflictTable />
      </div>
    );
  } catch (error) {
    return <ErrorState message={error instanceof Error ? error.message : "Unknown error"} title="Failed to load intelligence dashboard" />;
  }
}
