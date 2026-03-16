import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import type { SessionState } from "@/lib/types/auth";

const navigation = [
  { label: "Dashboard", href: "/admin" },
  { label: "Analytics", href: "/admin/analytics" },
  { label: "Products", href: "/admin/products" },
  { label: "Categories", href: "/admin/categories" },
  { label: "Images", href: "/admin/images" },
  { label: "Content", href: "/admin/content" },
  { label: "Integrations", href: "/admin/integrations" },
  { label: "Sync Monitor", href: "/admin/integrations/sync-monitor" },
  { label: "Settings", href: "/admin/settings" },
];

export function AdminShell({
  session,
  children,
}: {
  session: SessionState;
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#f3f5f8] text-ink">
      <div className="mx-auto grid min-h-screen max-w-7xl gap-6 px-4 py-6 lg:grid-cols-[17rem_minmax(0,1fr)] lg:px-8">
        <aside className="space-y-6">
          <Panel className="sticky top-6 overflow-hidden p-0">
            <div className="border-b border-slate-200 px-6 py-6">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-steel">Uniforma</p>
              <h1 className="mt-1 text-2xl font-semibold text-ink">Admin Console</h1>
              <p className="mt-2 text-sm text-slate-500">Catalog operations, supplier sync, and content control.</p>
            </div>
            <nav className="grid gap-1 p-3 text-sm">
              {navigation.map((item) => (
                <Link key={item.href} href={item.href} className="rounded-2xl px-4 py-3 font-medium text-slate-700 transition hover:bg-slate-100 hover:text-ink">
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="border-t border-slate-200 px-6 py-5">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant={session.user?.role === "admin" ? "success" : "info"}>{session.user?.role ?? "guest"}</Badge>
                <span className="text-sm text-slate-500">{session.user?.email ?? "Unauthenticated"}</span>
              </div>
              <form action="/api/auth/logout" method="post" className="mt-4">
                <button className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white" type="submit">
                  Log out
                </button>
              </form>
            </div>
          </Panel>
        </aside>
        <div className="space-y-6">
          <Panel className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-steel">Operations</p>
              <h2 className="mt-1 text-2xl font-semibold text-ink">Management interface</h2>
            </div>
            <div className="flex flex-wrap gap-3 text-sm text-slate-600">
              <span>Products</span>
              <span>Categories</span>
              <span>Images</span>
              <span>Integrations</span>
            </div>
          </Panel>
          {children}
        </div>
      </div>
    </div>
  );
}
