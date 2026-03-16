import SupplierSyncMonitor from "@/components/admin/supplier-sync-monitor";
import { ErrorState } from "@/components/ui/error-state";
import { Panel } from "@/components/ui/panel";
import { fetchSupplierSyncOverview } from "@/lib/api/server";
import { getSession } from "@/lib/auth/session";

export default async function AdminSupplierSyncPage() {
  const [overview, session] = await Promise.all([fetchSupplierSyncOverview(), getSession()]);

  if (!overview) {
    return <ErrorState title="Failed to load supplier sync monitor" message="Sync data is currently unavailable." />;
  }

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Integrations</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Supplier sync monitor</h2>
        <p className="mt-2 text-sm text-slate-600">Track supplier sync health, rerun imports, and inspect recent logs.</p>
      </Panel>
      <SupplierSyncMonitor initialOverview={overview} role={session.user?.role ?? "editor"} />
    </div>
  );
}
