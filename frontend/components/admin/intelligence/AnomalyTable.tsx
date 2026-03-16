"use client";

import Link from "next/link";

import { useDataQuality } from "@/hooks/useIntelligence";
import { Badge } from "@/components/ui/badge";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { Panel } from "@/components/ui/panel";
import type { DataQualityMetric, Severity } from "@/types/intelligence";

const badgeVariant: Record<Severity, "success" | "warning" | "danger"> = {
  healthy: "success",
  warning: "warning",
  critical: "danger",
  unavailable: "warning"
};

export function AnomalyTable() {
  const query = useDataQuality();

  if (query.isLoading) {
    return <LoadingState label="Loading data quality metrics" />;
  }

  if (query.isError || !query.data) {
    return <ErrorState title="Data quality unavailable" message="The dashboard could not load the aggregated quality metrics." />;
  }

  return (
    <Panel>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Data Quality</p>
          <h3 className="mt-1 text-xl font-semibold text-ink">Actionable anomalies</h3>
        </div>
        <p className="text-sm text-slate-500">Updated {new Date(query.data.generated_at).toLocaleString()}</p>
      </div>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Metric</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Count</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Severity</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {query.data.metrics.map((metric) => (
              <tr key={metric.key}>
                <td className="px-4 py-4">
                  <p className="font-semibold text-ink">{metric.label}</p>
                  <p className="mt-1 text-xs text-slate-500">{metric.description}</p>
                </td>
                <td className="px-4 py-4 text-slate-700">{metric.count}</td>
                <td className="px-4 py-4">
                  <Badge variant={badgeVariant[resolveSeverity(metric)]}>{resolveSeverity(metric)}</Badge>
                </td>
                <td className="px-4 py-4">
                  <Link className="text-clay underline" href={`/admin/products?filter=${encodeURIComponent(metric.filter)}`}>
                    Review products
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}

function resolveSeverity(metric: DataQualityMetric): Severity {
  if (metric.key === "variants_missing_ean") {
    if (metric.count > 100) return "critical";
    if (metric.count > 20) return "warning";
    return "healthy";
  }
  if (metric.key === "products_without_images") {
    if (metric.count > 200) return "critical";
    if (metric.count > 50) return "warning";
    return "healthy";
  }
  return metric.severity;
}
