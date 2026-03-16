import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AdminShell } from "@/components/layout/admin-shell";
import { getSession } from "@/lib/auth/session";

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = headers().get("x-pathname") ?? "";
  if (pathname.startsWith("/admin/login")) {
    return <>{children}</>;
  }

  const session = await getSession();
  if (!session.isAuthenticated) {
    redirect("/admin/login");
  }

  return <AdminShell session={session}>{children}</AdminShell>;
}
