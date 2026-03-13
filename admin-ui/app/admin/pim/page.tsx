import Link from "next/link";

import { Panel } from "@/components/ui/panel";
import { fetchPimImports, fetchPimSources } from "@/lib/api/server";

export default async function AdminPimPage() {
  const [sources, imports] = await Promise.all([fetchPimSources(), fetchPimImports()]);

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">PIM</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Import control</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 p-5">
            <p className="text-sm text-slate-500">Active sources</p>
            <p className="mt-2 text-3xl font-semibold text-ink">{sources.filter((source) => source.is_active).length}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 p-5">
            <p className="text-sm text-slate-500">Import runs</p>
            <p className="mt-2 text-3xl font-semibold text-ink">{imports.length}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 p-5">
            <p className="text-sm text-slate-500">Latest status</p>
            <p className="mt-2 text-3xl font-semibold text-ink">{imports[0]?.status ?? "none"}</p>
          </div>
        </div>
        <div className="mt-6 flex gap-3">
          <Link className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white" href="/admin/pim/sources">
            Sources
          </Link>
          <Link className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium" href="/admin/pim/imports">
            Import history
          </Link>
        </div>
      </Panel>
    </div>
  );
}
