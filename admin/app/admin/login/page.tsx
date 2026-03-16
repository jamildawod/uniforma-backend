import { redirect } from "next/navigation";

import { LoginForm } from "@/components/auth/login-form";
import { Panel } from "@/components/ui/panel";
import { getSession } from "@/lib/auth/session";

export default async function LoginPage() {
  const session = await getSession();
  if (session.isAuthenticated) {
    redirect("/admin/products");
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12">
      <Panel className="w-full max-w-md">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-steel">Uniforma</p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">Admin Login</h1>
        <p className="mt-2 text-sm text-slate-600">Sign in to manage product overrides, sync runs, and audit state.</p>
        <div className="mt-8">
          <LoginForm />
        </div>
      </Panel>
    </main>
  );
}
