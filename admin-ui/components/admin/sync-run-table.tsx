"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { Modal } from "@/components/ui/modal";
import type { SyncRun } from "@/lib/types/sync";

export function SyncRunTable({ runs }: { runs: SyncRun[] }) {
  const [selected, setSelected] = useState<SyncRun | null>(null);

  if (runs.length === 0) {
    return <EmptyState title="No sync runs" description="Trigger the first ingestion run to start audit history." />;
  }

  return (
    <>
      <div className="overflow-hidden rounded-3xl bg-white shadow-panel">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Started</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Finished</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Status</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Products</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Variants</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Images</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Error</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {runs.map((run) => (
              <tr key={run.id}>
                <td className="px-4 py-4">{new Date(run.started_at).toLocaleString()}</td>
                <td className="px-4 py-4">{run.finished_at ? new Date(run.finished_at).toLocaleString() : "Running"}</td>
                <td className="px-4 py-4">
                  <Badge variant={run.status === "success" ? "success" : run.status === "failed" ? "danger" : "warning"}>{run.status}</Badge>
                </td>
                <td className="px-4 py-4">{run.products_created + run.products_updated}</td>
                <td className="px-4 py-4">{run.variants_created + run.variants_updated}</td>
                <td className="px-4 py-4">{run.images_synced}</td>
                <td className="px-4 py-4">
                  {run.error_message ? (
                    <button className="text-clay underline" onClick={() => setSelected(run)} type="button">
                      View error
                    </button>
                  ) : (
                    <span className="text-slate-400">None</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Modal onClose={() => setSelected(null)} open={Boolean(selected)} title="Sync error details">
        <pre className="whitespace-pre-wrap rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">{selected?.error_message}</pre>
      </Modal>
    </>
  );
}
