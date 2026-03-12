import { redirect } from "next/navigation";

import { AdminShell } from "@/components/layout/admin-shell";
import { getSession } from "@/lib/auth/session";

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const session = await getSession();
  if (!session.isAuthenticated) {
    redirect("/admin/login");
  }

  return <AdminShell session={session}>{children}</AdminShell>;
}
