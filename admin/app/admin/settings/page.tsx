import Link from "next/link";

import { Panel } from "@/components/ui/panel";

const items = [
  { title: "Integrations", href: "/admin/settings/integrations", description: "FTP settings, credentials, and sync controls." },
  { title: "Sync monitor", href: "/admin/integrations/sync-monitor", description: "Recent supplier sync logs and status." },
  { title: "Content", href: "/admin/content", description: "Homepage and contact copy settings." },
];

export default function AdminSettingsPage() {
  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Settings</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Admin settings</h2>
      </Panel>
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <Link key={item.href} href={item.href} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-panel transition hover:-translate-y-0.5">
            <p className="text-lg font-semibold text-ink">{item.title}</p>
            <p className="mt-2 text-sm text-slate-600">{item.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
