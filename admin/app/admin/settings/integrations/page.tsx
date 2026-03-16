import Link from "next/link";

import { HejcoIntegrationForm } from "@/components/admin/hejco-integration-form";
import { Panel } from "@/components/ui/panel";
import { fetchHejcoIntegration, fetchSupplierSyncOverview } from "@/lib/api/server";

export default async function AdminIntegrationsPage() {
  const [integration, overview] = await Promise.all([fetchHejcoIntegration(), fetchSupplierSyncOverview()]);

  return (
    <div className="space-y-6">
      <Panel>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Settings</p>
            <h2 className="mt-1 text-2xl font-semibold text-ink">Hejco integration</h2>
            <p className="mt-2 text-sm text-slate-500">Manage FTP connection settings for nightly imports and on-demand syncs without changing code.</p>
          </div>
          <Link className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium" href="/admin/integrations/sync-monitor">
            Open sync monitor
          </Link>
        </div>
      </Panel>
      {integration ? <HejcoIntegrationForm initial={integration} /> : null}
      {overview ? (
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Latest sync summary</p>
          <div className="mt-4 grid gap-3 text-sm text-slate-600 md:grid-cols-2 xl:grid-cols-4">
            <p>Supplier: {overview.supplier}</p>
            <p>Status: {overview.last_sync_status ?? "Unknown"}</p>
            <p>Last run: {overview.last_sync_time ? new Date(overview.last_sync_time).toLocaleString() : "Never"}</p>
            <p>Products imported: {overview.products_imported ?? 0}</p>
          </div>
        </Panel>
      ) : null}
    </div>
  );
}
