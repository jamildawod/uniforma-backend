"use client";

import { useState, useTransition } from "react";

import { updateAdminContent } from "@/lib/api/client";
import type { SiteContent } from "@/lib/types/content";

export function ContentEditor({ initial }: { initial: SiteContent }) {
  const [form, setForm] = useState<SiteContent>(initial);
  const [message, setMessage] = useState("");
  const [pending, startTransition] = useTransition();

  function update<K extends keyof SiteContent>(key: K, value: SiteContent[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function save() {
    startTransition(async () => {
      setMessage("");
      try {
        const next = await updateAdminContent(form);
        setForm(next);
        setMessage("Content updated.");
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Failed to save content.");
      }
    });
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-6">
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" value={form.hero_title} onChange={(event) => update("hero_title", event.target.value)} placeholder="Hero title" />
        <textarea className="min-h-28 rounded-2xl border border-slate-200 px-4 py-3 text-sm" value={form.hero_body} onChange={(event) => update("hero_body", event.target.value)} placeholder="Hero body" />
        <textarea className="min-h-24 rounded-2xl border border-slate-200 px-4 py-3 text-sm" value={form.homepage_categories.join("\n")} onChange={(event) => update("homepage_categories", event.target.value.split(/\n+/).map((item) => item.trim()).filter(Boolean))} placeholder="Homepage categories, one per line" />
        <textarea className="min-h-32 rounded-2xl border border-slate-200 px-4 py-3 text-sm" value={form.company_information} onChange={(event) => update("company_information", event.target.value)} placeholder="Company information" />
        <textarea className="min-h-28 rounded-2xl border border-slate-200 px-4 py-3 text-sm" value={form.contact_text} onChange={(event) => update("contact_text", event.target.value)} placeholder="Contact text" />
        <div>
          <button className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white" disabled={pending} onClick={save} type="button">{pending ? "Saving..." : "Save content"}</button>
        </div>
      </div>
      {message ? <p className="text-sm text-slate-600">{message}</p> : null}
    </div>
  );
}
