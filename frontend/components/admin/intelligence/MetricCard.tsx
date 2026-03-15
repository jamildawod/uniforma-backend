import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import type { Severity } from "@/types/intelligence";

const severityMap: Record<Severity, "success" | "warning" | "danger"> = {
  healthy: "success",
  warning: "warning",
  critical: "danger",
  unavailable: "warning"
};

export function MetricCard({
  title,
  value,
  detail,
  severity,
  href
}: {
  title: string;
  value: string | number;
  detail: string;
  severity: Severity;
  href?: string;
}) {
  const content = (
    <Panel className="h-full">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-steel">{title}</p>
          <p className="mt-3 text-3xl font-semibold text-ink">{value}</p>
          <p className="mt-2 text-sm text-slate-600">{detail}</p>
        </div>
        <Badge variant={severityMap[severity]}>{severity}</Badge>
      </div>
    </Panel>
  );

  if (!href) {
    return content;
  }

  return (
    <Link className="block h-full" href={href}>
      {content}
    </Link>
  );
}
