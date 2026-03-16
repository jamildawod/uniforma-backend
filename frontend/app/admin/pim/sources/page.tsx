import { PimSourceManager } from "@/components/admin/pim-source-manager";
import { Panel } from "@/components/ui/panel";
import { fetchPimSources } from "@/lib/api/server";

export default async function AdminPimSourcesPage() {
  const sources = await fetchPimSources();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">PIM Sources</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Source management</h2>
        <div className="mt-6">
          <PimSourceManager sources={sources} />
        </div>
      </Panel>
    </div>
  );
}
