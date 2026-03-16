import { SyncMonitorPanel } from "@/components/admin/sync-monitor-panel";
import { Panel } from "@/components/ui/panel";
import { fetchSupplierSyncOverview } from "@/lib/api/server";

export default async function AdminSyncMonitorPage() {
  const overview = await fetchSupplierSyncOverview();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Integrations</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Supplier sync monitor</h2>
        <p className="mt-2 text-sm text-slate-600">Track supplier import health, imported products, and recent error logs.</p>
      </Panel>
      {overview ? <SyncMonitorPanel overview={overview} /> : null}
    </div>
  );
}
