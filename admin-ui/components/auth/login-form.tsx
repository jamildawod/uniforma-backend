"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { loginRequest } from "@/lib/api/client";
import { loginSchema, type LoginInput } from "@/lib/schemas/auth";

export function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const form = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: ""
    }
  });

  return (
    <form
      className="grid gap-4"
      onSubmit={form.handleSubmit(async (values) => {
        setError(null);
        try {
          await loginRequest(values);
          router.push("/admin/products");
          router.refresh();
        } catch (nextError) {
          setError(nextError instanceof Error ? nextError.message : "Login failed.");
        }
      })}
    >
      <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Email" {...form.register("email")} />
      <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Password" type="password" {...form.register("password")} />
      <button className="rounded-2xl bg-ink px-4 py-3 text-sm font-semibold text-white" disabled={form.formState.isSubmitting} type="submit">
        {form.formState.isSubmitting ? "Signing in..." : "Sign in"}
      </button>
      {error ? <p className="text-sm text-rose-600">{error}</p> : null}
    </form>
  );
}
