"use client";

import { useState } from "react";

import { createQuoteRequest } from "@/lib/api/client";

type QuoteFormProps = {
  defaultMessage?: string;
  title?: string;
  compact?: boolean;
  productId?: string;
  variantId?: number;
};

export function QuoteForm({
  defaultMessage = "",
  title = "Begär offert",
  compact = false,
  productId,
  variantId
}: QuoteFormProps) {
  const [form, setForm] = useState({
    name: "",
    email: "",
    company: "",
    message: defaultMessage
  });
  const [state, setState] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState(null);
    setIsSubmitting(true);
    try {
      await createQuoteRequest({
        product_id: productId ?? null,
        variant_id: variantId ?? null,
        name: form.name,
        email: form.email,
        company: form.company || null,
        message: form.message
      });
      setForm({
        name: "",
        email: "",
        company: "",
        message: defaultMessage
      });
      setState({ message: "Offertförfrågan skickad.", type: "success" });
    } catch (error) {
      setState({ message: error instanceof Error ? error.message : "Något gick fel.", type: "error" });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className={`rounded-[2rem] border border-white/10 bg-white p-6 shadow-2xl ${compact ? "" : "lg:p-8"}`}>
      <div className="mb-5">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#f28b39]">Kontakt</p>
        <h3 className="mt-2 text-2xl font-semibold text-[#10233f]">{title}</h3>
      </div>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="grid gap-4 md:grid-cols-2">
          <input
            className="rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900"
            onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
            placeholder="Namn"
            required
            value={form.name}
          />
          <input
            className="rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900"
            onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
            placeholder="E-post"
            required
            type="email"
            value={form.email}
          />
        </div>
        <input
          className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900"
          onChange={(event) => setForm((current) => ({ ...current, company: event.target.value }))}
          placeholder="Företag"
          value={form.company}
        />
        <textarea
          className="min-h-32 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900"
          onChange={(event) => setForm((current) => ({ ...current, message: event.target.value }))}
          placeholder="Berätta vad ni behöver hjälp med"
          required
          value={form.message}
        />
        <button
          className="rounded-full bg-[#f28b39] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#dd7621]"
          disabled={isSubmitting}
          type="submit"
        >
          {isSubmitting ? "Skickar..." : "Skicka offertförfrågan"}
        </button>
        {state ? (
          <p className={`text-sm ${state.type === "success" ? "text-emerald-600" : "text-red-600"}`}>{state.message}</p>
        ) : null}
      </form>
    </div>
  );
}
