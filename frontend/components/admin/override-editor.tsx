"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { usePatchProductOverride } from "@/hooks/use-product-mutations";
import { overrideFieldsSchema, type OverrideFieldsInput } from "@/lib/schemas/overrides";
import type { AdminProduct } from "@/lib/types/products";

export function OverrideEditor({ product }: { product: AdminProduct }) {
  const mutation = usePatchProductOverride(product.id);
  const [message, setMessage] = useState<string | null>(null);
  const form = useForm<OverrideFieldsInput>({
    resolver: zodResolver(overrideFieldsSchema),
    defaultValues: {
      name: typeof product.applied_overrides.name === "string" ? product.applied_overrides.name : "",
      description: typeof product.applied_overrides.description === "string" ? product.applied_overrides.description : "",
      brand: typeof product.applied_overrides.brand === "string" ? product.applied_overrides.brand : ""
    }
  });

  return (
    <form
      className="grid gap-4"
      onSubmit={form.handleSubmit(async (values) => {
        setMessage(null);
        const payload = Object.fromEntries(
          Object.entries(values).map(([key, value]) => [key, value === "" ? null : value])
        );
        try {
          await mutation.mutateAsync({ overrides: payload });
          setMessage("Overrides saved.");
        } catch (error) {
          setMessage(error instanceof Error ? error.message : "Failed to save overrides.");
        }
      })}
    >
      <div className="grid gap-2">
        <label className="text-sm font-medium text-slate-700">Name override</label>
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" {...form.register("name")} />
      </div>
      <div className="grid gap-2">
        <label className="text-sm font-medium text-slate-700">Description override</label>
        <textarea className="min-h-32 rounded-2xl border border-slate-200 px-4 py-3 text-sm" {...form.register("description")} />
      </div>
      <div className="grid gap-2">
        <label className="text-sm font-medium text-slate-700">Brand override</label>
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" {...form.register("brand")} />
      </div>
      <div className="flex items-center gap-3">
        <button className="rounded-2xl bg-clay px-4 py-3 text-sm font-semibold text-white" disabled={mutation.isPending} type="submit">
          {mutation.isPending ? "Saving..." : "Save overrides"}
        </button>
        {message ? <span className="text-sm text-slate-600">{message}</span> : null}
      </div>
    </form>
  );
}
