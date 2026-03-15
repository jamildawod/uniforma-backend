"use client";

import { useState } from "react";
import Link from "next/link";

import { useOverrideConflicts } from "@/hooks/useIntelligence";
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

export function OverrideConflictTable() {
  const [page, setPage] = useState(1);
  const query = useOverrideConflicts({ page, pageSize: 10 });

  if (query.isLoading) {
    return <LoadingState label="Loading override conflicts" />;
  }

  if (query.isError || !query.data) {
    return <ErrorState title="Override conflicts unavailable" message="The dashboard could not load conflict diagnostics." />;
  }

  return (
    <Panel>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Override Conflicts</p>
          <h3 className="mt-1 text-xl font-semibold text-ink">Conflicting admin overrides</h3>
        </div>
        <p className="text-sm text-slate-500">{query.data.total} total conflicts</p>
      </div>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Product</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Field</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">PIM</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Override</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Severity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {query.data.conflicts.map((conflict) => (
              <tr key={conflict.id}>
                <td className="px-4 py-4">
                  <Link className="font-semibold text-ink" href={`/admin/products/${conflict.product_id}`}>
                    {conflict.product_name}
                  </Link>
                </td>
                <td className="px-4 py-4 text-slate-700">{conflict.field_name}</td>
                <td className="px-4 py-4 text-slate-600">{conflict.source_value ?? "—"}</td>
                <td className="px-4 py-4 text-slate-600">{conflict.override_value ?? "—"}</td>
                <td className="px-4 py-4">
                  <Badge variant={severityMap[conflict.severity]}>{conflict.severity}</Badge>
                </td>
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
