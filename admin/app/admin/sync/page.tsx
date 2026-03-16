import { SyncRunTable } from "@/components/admin/sync-run-table";
import { SyncTriggerCard } from "@/components/admin/sync-trigger-card";
import { ErrorState } from "@/components/ui/error-state";
import { Panel } from "@/components/ui/panel";
import { fetchSyncRuns } from "@/lib/api/server";
import { getSession } from "@/lib/auth/session";

export default async function AdminSyncPage() {
  const session = await getSession();

  try {
    const runs = await fetchSyncRuns();

    return (
      <div className="space-y-6">
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Operations</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">PIM Sync</h2>
          <p className="mt-2 text-sm text-slate-600">Monitor sync history and trigger controlled ingestion runs.</p>
        </Panel>
        <SyncTriggerCard role={session.user?.role ?? "editor"} />
        <SyncRunTable runs={runs} />
      </div>
    );
  } catch (error) {
    return <ErrorState message={error instanceof Error ? error.message : "Unknown error"} title="Failed to load sync runs" />;
  }
}
