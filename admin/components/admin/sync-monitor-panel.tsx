"use client";

import { useState, useTransition } from "react";

import { syncHejcoIntegration } from "@/lib/api/client";
import type { SupplierSyncOverview } from "@/lib/types/pim";

export function SyncMonitorPanel({ overview }: { overview: SupplierSyncOverview }) {
  const [message, setMessage] = useState("");
  const [pending, startTransition] = useTransition();

  function runSync() {
    startTransition(async () => {
      setMessage("");
      try {
        const result = await syncHejcoIntegration();
        setMessage(result.message || `Sync completed. Imported ${result.products_imported + result.products_updated} products.`);
        window.location.reload();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Sync failed.");
      }
    });
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-3xl border border-slate-200 bg-white p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Supplier</p>
          <p className="mt-3 text-2xl font-semibold text-ink">{overview.supplier}</p>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Last sync time</p>
          <p className="mt-3 text-sm font-semibold text-ink">{overview.last_sync_time ? new Date(overview.last_sync_time).toLocaleString() : "Never"}</p>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Sync status</p>
          <p className="mt-3 text-2xl font-semibold capitalize text-ink">{overview.last_sync_status || "unknown"}</p>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Products imported</p>
          <p className="mt-3 text-4xl font-semibold text-ink">{overview.products_imported ?? 0}</p>
        </div>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Run supplier sync</p>
            <p className="mt-2 text-sm text-slate-600">Trigger an on-demand Hejco synchronization using the current FTP configuration.</p>
          </div>
          <button className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white" disabled={pending} onClick={runSync} type="button">
            {pending ? "Running..." : "Run Sync Now"}
          </button>
        </div>
        {message ? <p className="mt-4 text-sm text-slate-600">{message}</p> : null}
        {overview.errors ? <p className="mt-4 text-sm text-red-600">Latest error: {overview.errors}</p> : null}
      </div>

      <div className="overflow-hidden rounded-3xl bg-white shadow-panel">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Started</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Finished</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Status</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Products</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Images</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Errors</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {overview.logs.map((log) => (
              <tr key={log.id}>
                <td className="px-4 py-4">{new Date(log.started_at).toLocaleString()}</td>
                <td className="px-4 py-4">{log.finished_at ? new Date(log.finished_at).toLocaleString() : "Running"}</td>
                <td className="px-4 py-4 capitalize">{log.status}</td>
                <td className="px-4 py-4">{log.products_imported}</td>
                <td className="px-4 py-4">{log.images_downloaded}</td>
                <td className="px-4 py-4 text-slate-500">{log.error_message || "None"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
