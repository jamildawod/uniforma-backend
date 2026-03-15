"use client";

import { useState, useTransition } from "react";

import { createPimSource, runPimImport, testPimSource } from "@/lib/api/client";
import type { PimSource, PimSourcePayload } from "@/lib/types/pim";

const initialForm: PimSourcePayload = {
  name: "",
  type: "local",
  path: "/app/sample_products.csv",
  schedule: "0 2 * * *",
  is_active: true
};

export function PimSourceManager({ sources }: { sources: PimSource[] }) {
  const [form, setForm] = useState<PimSourcePayload>(initialForm);
  const [message, setMessage] = useState<string>("");
  const [pending, startTransition] = useTransition();

  function update<K extends keyof PimSourcePayload>(key: K, value: PimSourcePayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function submit() {
    startTransition(async () => {
      try {
        await createPimSource(form);
        setMessage("Source created.");
        window.location.reload();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Failed to create source.");
      }
    });
  }

  function runImport(sourceId: number) {
    startTransition(async () => {
      try {
        const result = await runPimImport(sourceId);
        setMessage(`Import finished. Processed ${result.records_processed} records.`);
        window.location.reload();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Import failed.");
      }
    });
  }

  function testConnection(sourceId: number) {
    startTransition(async () => {
      try {
        const result = await testPimSource(sourceId);
        setMessage(result.ok ? "Connection test succeeded." : "Connection test failed.");
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Connection test failed.");
      }
    });
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-6 md:grid-cols-2">
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          placeholder="Source name"
          value={form.name ?? ""}
          onChange={(event) => update("name", event.target.value)}
        />
        <select
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          value={form.type}
          onChange={(event) => update("type", event.target.value as PimSourcePayload["type"])}
        >
          <option value="local">Local</option>
          <option value="http">HTTP</option>
          <option value="ftp">FTP</option>
          <option value="sftp">SFTP</option>
        </select>
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          placeholder="Host"
          value={form.host ?? ""}
          onChange={(event) => update("host", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          placeholder="Port"
          value={form.port ?? ""}
          onChange={(event) => update("port", event.target.value ? Number(event.target.value) : null)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          placeholder="Username"
          value={form.username ?? ""}
          onChange={(event) => update("username", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          placeholder="Password"
          type="password"
          value={form.password ?? ""}
          onChange={(event) => update("password", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm md:col-span-2"
          placeholder="Path or URL"
          value={form.path ?? ""}
          onChange={(event) => update("path", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          placeholder="File pattern"
          value={form.file_pattern ?? ""}
          onChange={(event) => update("file_pattern", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          placeholder="Schedule"
          value={form.schedule ?? ""}
          onChange={(event) => update("schedule", event.target.value)}
        />
        <button
          className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white md:col-span-2"
          disabled={pending}
          onClick={submit}
          type="button"
        >
          Add source
        </button>
      </div>

      {message ? <p className="text-sm text-slate-600">{message}</p> : null}

      <div className="space-y-4">
        {sources.map((source) => (
          <article key={source.id} className="rounded-3xl border border-slate-200 bg-white p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-steel">{source.type}</p>
                <h3 className="mt-2 text-xl font-semibold text-ink">{source.name}</h3>
                <p className="mt-2 text-sm text-slate-500">{source.path || source.host || "No path configured"}</p>
              </div>
              <div className="flex gap-3">
                <button
                  className="rounded-full border border-slate-200 px-4 py-2 text-sm"
                  disabled={pending}
                  onClick={() => testConnection(source.id)}
                  type="button"
                >
                  Test
                </button>
                <button
                  className="rounded-full bg-[#10233f] px-4 py-2 text-sm font-semibold text-white"
                  disabled={pending}
                  onClick={() => runImport(source.id)}
                  type="button"
                >
                  Run import
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
