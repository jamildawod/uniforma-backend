"use client";

import { useState } from "react";

import { useTriggerSync } from "@/hooks/use-product-mutations";
import type { UserRole } from "@/lib/types/auth";

export function SyncTriggerCard({ role }: { role: UserRole }) {
  const mutation = useTriggerSync();
  const [message, setMessage] = useState<string | null>(null);
  const isDisabled = role !== "admin";

  return (
    <div className="rounded-3xl bg-white p-6 shadow-panel">
      <h2 className="text-lg font-semibold text-ink">Manual sync</h2>
      <p className="mt-2 text-sm text-slate-600">Runs PIM ingestion and image synchronization through the same backend orchestration path as the scheduler.</p>
      <div className="mt-4 flex items-center gap-3">
        <button
          className="rounded-2xl bg-ink px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
          disabled={isDisabled || mutation.isPending}
          onClick={async () => {
            setMessage(null);
            try {
              const result = await mutation.mutateAsync();
              setMessage(`Sync completed. ${result.products_created} created, ${result.products_updated} updated.`);
            } catch (error) {
              setMessage(error instanceof Error ? error.message : "Sync failed.");
            }
          }}
          type="button"
        >
          {mutation.isPending ? "Running..." : "Trigger sync"}
        </button>
        {isDisabled ? <span className="text-sm text-slate-500">Admin role required.</span> : null}
      </div>
      {message ? <p className="mt-3 text-sm text-slate-600">{message}</p> : null}
    </div>
  );
}
