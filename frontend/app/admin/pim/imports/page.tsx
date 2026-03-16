import { Panel } from "@/components/ui/panel";
import { fetchPimImports } from "@/lib/api/server";

export default async function AdminPimImportsPage() {
  const imports = await fetchPimImports();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">PIM Imports</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Import history</h2>
        <div className="mt-6 space-y-4">
          {imports.map((run) => (
            <article key={run.id} className="rounded-2xl border border-slate-200 p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-ink">{run.source?.name ?? "Unknown source"}</h3>
                  <p className="text-sm text-slate-500">
                    Processed {run.records_processed} / created {run.records_created} / updated {run.records_updated}
                  </p>
                </div>
                <div className="text-right text-sm text-slate-500">
                  <p className="uppercase tracking-[0.16em]">{run.status}</p>
                  <p>{new Date(run.started_at).toLocaleString()}</p>
                </div>
              </div>
              {run.error_log ? <p className="mt-4 text-sm text-rose-600">{run.error_log}</p> : null}
            </article>
          ))}
          {imports.length === 0 ? <p className="text-sm text-slate-500">No PIM import runs available.</p> : null}
        </div>
      </Panel>
    </div>
  );
}
