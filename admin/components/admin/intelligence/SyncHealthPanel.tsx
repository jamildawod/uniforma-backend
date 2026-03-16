"use client";

import { useState } from "react";

import { useSyncHealth } from "@/hooks/useIntelligence";
import { Badge } from "@/components/ui/badge";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { Panel } from "@/components/ui/panel";
import type { Severity } from "@/types/intelligence";

const severityMap: Record<Severity, "success" | "warning" | "danger"> = {
  healthy: "success",
  warning: "warning",
  critical: "danger",
  unavailable: "warning"
};

export function SyncHealthPanel() {
  const [page, setPage] = useState(1);
  const query = useSyncHealth({ page, pageSize: 10 });

  if (query.isLoading) {
    return <LoadingState label="Loading sync health" />;
  }

  if (query.isError || !query.data) {
    return <ErrorState title="Sync health unavailable" message="Recent ingestion health could not be loaded." />;
  }

  return (
    <Panel>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Sync Health</p>
          <h3 className="mt-1 text-xl font-semibold text-ink">Recent sync runs</h3>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={severityMap[query.data.status]}>{query.data.status}</Badge>
          <p className="text-sm text-slate-500">
            Last success {query.data.last_successful_sync_at ? new Date(query.data.last_successful_sync_at).toLocaleString() : "N/A"}
          </p>
        </div>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Running syncs</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{query.data.running_syncs}</p>
        </div>
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Failed last 24h</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{query.data.failed_runs_last_24h}</p>
        </div>
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Visible runs</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{query.data.recent_runs.length}</p>
        </div>
      </div>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Started</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Status</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Products</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Variants</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Images</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {query.data.recent_runs.map((run) => (
              <tr key={run.id}>
                <td className="px-4 py-4">{new Date(run.started_at).toLocaleString()}</td>
                <td className="px-4 py-4">
                  <Badge variant={run.status === "success" ? "success" : run.status === "failed" ? "danger" : "warning"}>
                    {run.status}
                  </Badge>
                </td>
                <td className="px-4 py-4">{run.products_created + run.products_updated}</td>
                <td className="px-4 py-4">{run.variants_created + run.variants_updated}</td>
                <td className="px-4 py-4">{run.images_synced}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
        <span>Page {query.data.page}</span>
        <div className="flex gap-2">
          <button className="rounded-full border border-slate-200 px-3 py-1 disabled:opacity-40" disabled={page <= 1} onClick={() => setPage((current) => current - 1)} type="button">
            Previous
          </button>
          <button
            className="rounded-full border border-slate-200 px-3 py-1 disabled:opacity-40"
            disabled={query.data.page * query.data.page_size >= query.data.total}
            onClick={() => setPage((current) => current + 1)}
            type="button"
          >
            Next
          </button>
        </div>
      </div>
    </Panel>
  );
}
