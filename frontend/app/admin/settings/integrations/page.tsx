import { HejcoIntegrationForm } from "@/components/admin/hejco-integration-form";
import { Panel } from "@/components/ui/panel";
import { fetchHejcoIntegration } from "@/lib/api/server";

export default async function AdminIntegrationsPage() {
  const integration = await fetchHejcoIntegration();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Settings</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Hejco integration</h2>
        <p className="mt-2 text-sm text-slate-500">
          Manage FTP connection settings for nightly imports and on-demand syncs without changing code.
        </p>
      </Panel>
      {integration ? <HejcoIntegrationForm initial={integration} /> : null}
    </div>
  );
}
