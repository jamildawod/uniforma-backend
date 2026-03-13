import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import type { SessionState } from "@/lib/types/auth";

export function AdminShell({
  session,
  children
}: {
  session: SessionState;
  children: React.ReactNode;
}) {
  return (
    <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-4 py-6 lg:px-8">
      <Panel className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-steel">Uniforma</p>
          <h1 className="mt-1 text-2xl font-semibold text-ink">Admin Console</h1>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <nav className="flex flex-wrap gap-4 text-sm">
            <Link href="/admin">Dashboard</Link>
            <Link href="/admin/products">Products</Link>
            <Link href="/admin/brands">Brands</Link>
            <Link href="/admin/categories">Categories</Link>
            <Link href="/admin/media">Media</Link>
            <Link href="/admin/pim">PIM</Link>
            <Link href="/admin/quotes">Quotes</Link>
            <Link href="/admin/intelligence">Intelligence</Link>
            <Link href="/admin/sync">Sync</Link>
          </nav>
          <Badge variant={session.user?.role === "admin" ? "success" : "info"}>{session.user?.role ?? "guest"}</Badge>
          <span className="text-sm text-slate-500">{session.user?.email ?? "Unauthenticated"}</span>
          <form action="/api/auth/logout" method="post">
            <button className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white" type="submit">
              Log out
            </button>
          </form>
        </div>
      </Panel>
      {children}
    </div>
  );
}
