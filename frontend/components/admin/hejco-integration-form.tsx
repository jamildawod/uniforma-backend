"use client";

import { useState, useTransition } from "react";

import { syncHejcoIntegration, testHejcoIntegration, updateHejcoIntegration } from "@/lib/api/client";
import type { HejcoIntegrationPayload, HejcoIntegrationSetting } from "@/lib/types/pim";

export function HejcoIntegrationForm({ initial }: { initial: HejcoIntegrationSetting }) {
  const [form, setForm] = useState<HejcoIntegrationPayload>({
    provider: initial.provider,
    ftp_host: initial.ftp_host || "partnerftp.hejco.com",
    ftp_username: initial.ftp_username,
    ftp_password: "",
    pictures_path: initial.pictures_path,
    product_data_path: initial.product_data_path,
    stock_path: initial.stock_path,
    sync_enabled: initial.sync_enabled,
    sync_hour: initial.sync_hour,
    timeout_seconds: initial.timeout_seconds
  });
  const [message, setMessage] = useState("");
  const [pending, startTransition] = useTransition();

  function update<K extends keyof HejcoIntegrationPayload>(key: K, value: HejcoIntegrationPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function save() {
    startTransition(async () => {
      try {
        const result = await updateHejcoIntegration(form);
        setMessage(`Saved settings for ${result.provider}.`);
        setForm((current) => ({ ...current, ftp_password: "" }));
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Failed to save settings.");
      }
    });
  }

  function testConnection() {
    startTransition(async () => {
      try {
        const result = await testHejcoIntegration();
        setMessage(result.message);
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Connection test failed.");
      }
    });
  }

  function syncNow() {
    startTransition(async () => {
      try {
        const result = await syncHejcoIntegration();
        setMessage(result.message || `Sync completed. Imported ${result.products_imported + result.products_updated} products.`);
        window.location.reload();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Sync failed.");
      }
    });
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-6 md:grid-cols-2">
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" value={form.provider ?? "Hejco"} disabled />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          placeholder="FTP host"
          value={form.ftp_host}
          onChange={(event) => update("ftp_host", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          placeholder="FTP username"
          value={form.ftp_username ?? ""}
          onChange={(event) => update("ftp_username", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          type="password"
          placeholder={initial.has_password ? "********" : "FTP password"}
          value={form.ftp_password ?? ""}
          onChange={(event) => update("ftp_password", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm md:col-span-2"
          placeholder="Pictures path"
          value={form.pictures_path}
          onChange={(event) => update("pictures_path", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm md:col-span-2"
          placeholder="Product data path"
          value={form.product_data_path}
          onChange={(event) => update("product_data_path", event.target.value)}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm md:col-span-2"
          placeholder="Stock path"
          value={form.stock_path}
          onChange={(event) => update("stock_path", event.target.value)}
        />
        <label className="flex items-center gap-3 rounded-2xl border border-slate-200 px-4 py-3 text-sm">
          <input
            type="checkbox"
            checked={form.sync_enabled}
            onChange={(event) => update("sync_enabled", event.target.checked)}
          />
          Automatic sync enabled
        </label>
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          type="number"
          min={0}
          max={23}
          placeholder="Sync hour"
          value={form.sync_hour}
          onChange={(event) => update("sync_hour", Number(event.target.value))}
        />
        <input
          className="rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          type="number"
          min={5}
          max={600}
          placeholder="Timeout seconds"
          value={form.timeout_seconds}
          onChange={(event) => update("timeout_seconds", Number(event.target.value))}
        />
        <div className="flex flex-wrap gap-3 md:col-span-2">
          <button className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white" disabled={pending} onClick={save} type="button">
            Save settings
          </button>
          <button className="rounded-full border border-slate-200 px-5 py-3 text-sm font-semibold" disabled={pending} onClick={testConnection} type="button">
            Test connection
          </button>
          <button className="rounded-full border border-[#10233f] bg-[#10233f] px-5 py-3 text-sm font-semibold text-white" disabled={pending} onClick={syncNow} type="button">
            Sync now
          </button>
        </div>
      </div>

      {message ? <p className="text-sm text-slate-600">{message}</p> : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Last successful sync</p>
          <p className="mt-2 text-sm font-semibold text-ink">
            {initial.last_sync_status === "success" ? initial.last_sync_at || "Never" : "Never"}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Last failed sync</p>
          <p className="mt-2 text-sm font-semibold text-ink">
            {initial.last_sync_status === "failed" ? initial.last_sync_at || "Never" : "None"}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Sync status</p>
          <p className="mt-2 text-sm font-semibold text-ink">{initial.last_sync_status || "Not run"}</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Last imported product count</p>
          <p className="mt-2 text-sm font-semibold text-ink">{initial.last_imported_product_count ?? 0}</p>
        </div>
      </div>
      {initial.last_sync_message ? <p className="text-sm text-slate-500">{initial.last_sync_message}</p> : null}
    </div>
  );
}
