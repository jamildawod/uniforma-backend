"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useTransition } from "react";

export function ProductFilterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  return (
    <form
      className="grid gap-4 md:grid-cols-5"
      onSubmit={(event) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const params = new URLSearchParams(searchParams.toString());
        for (const [key, value] of formData.entries()) {
          if (!value || value === "all") {
            params.delete(key);
          } else {
            params.set(key, String(value));
          }
        }
        params.set("page", "1");
        startTransition(() => {
          router.push(`/admin/products?${params.toString()}`);
        });
      }}
    >
      <input
        className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
        defaultValue={searchParams.get("search") ?? ""}
        name="search"
        placeholder="Search by name or SKU"
      />
      <select className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" defaultValue={searchParams.get("isActive") ?? "all"} name="isActive">
        <option value="all">All activity</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
      <select className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" defaultValue={searchParams.get("deleted") ?? "all"} name="deleted">
        <option value="all">All lifecycle</option>
        <option value="not_deleted">Not deleted</option>
        <option value="deleted">Deleted</option>
      </select>
      <select className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" defaultValue={searchParams.get("hasOverride") ?? "all"} name="hasOverride">
        <option value="all">All override states</option>
        <option value="yes">Has override</option>
        <option value="no">No override</option>
      </select>
      <button className="rounded-2xl bg-clay px-4 py-3 text-sm font-semibold text-white disabled:opacity-60" disabled={isPending} type="submit">
        {isPending ? "Applying..." : "Apply Filters"}
      </button>
    </form>
  );
}
