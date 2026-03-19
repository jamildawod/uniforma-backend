"use client";

import { useState } from "react";

export default function KontaktPage() {
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    // TODO: wire up to backend/email service
    setSubmitted(true);
  }

  return (
    <div className="min-h-screen bg-stone-50 text-stone-950">
      <main className="mx-auto max-w-3xl px-6 py-16">

        <div className="mb-10 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-stone-400">
            Kom i kontakt
          </p>
          <h1 className="mt-2 text-4xl font-bold leading-tight text-stone-950">
            Kontakta oss
          </h1>
          <p className="mt-4 text-base text-stone-600">
            Berätta vad ni söker så återkommer vi med ett förslag och offert
            anpassad efter era behov.
          </p>
        </div>

        {submitted ? (
          <div className="rounded-2xl border border-green-200 bg-green-50 p-10 text-center shadow-sm">
            <p className="text-2xl font-semibold text-green-800">Tack för din förfrågan!</p>
            <p className="mt-3 text-stone-600">
              Vi återkommer till dig inom kort.
            </p>
          </div>
        ) : (
          <form
            onSubmit={handleSubmit}
            className="space-y-6 rounded-2xl border border-stone-200 bg-white p-8 shadow-sm"
          >
            <div className="grid gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="namn" className="mb-1.5 block text-sm font-semibold text-stone-700">
                  Namn <span className="text-red-500">*</span>
                </label>
                <input
                  id="namn"
                  name="namn"
                  type="text"
                  required
                  placeholder="Ditt namn"
                  className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:bg-white focus:outline-none"
                />
              </div>
              <div>
                <label htmlFor="foretag" className="mb-1.5 block text-sm font-semibold text-stone-700">
                  Företag <span className="text-red-500">*</span>
                </label>
                <input
                  id="foretag"
                  name="foretag"
                  type="text"
                  required
                  placeholder="Företagsnamn"
                  className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:bg-white focus:outline-none"
                />
              </div>
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="epost" className="mb-1.5 block text-sm font-semibold text-stone-700">
                  E-post <span className="text-red-500">*</span>
                </label>
                <input
                  id="epost"
                  name="epost"
                  type="email"
                  required
                  placeholder="din@epost.se"
                  className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:bg-white focus:outline-none"
                />
              </div>
              <div>
                <label htmlFor="telefon" className="mb-1.5 block text-sm font-semibold text-stone-700">
                  Telefonnummer
                </label>
                <input
                  id="telefon"
                  name="telefon"
                  type="tel"
                  placeholder="+46 70 000 00 00"
                  className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:bg-white focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label htmlFor="amne" className="mb-1.5 block text-sm font-semibold text-stone-700">
                Ämne
              </label>
              <select
                id="amne"
                name="amne"
                className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm text-stone-900 focus:border-stone-500 focus:bg-white focus:outline-none"
              >
                <option value="">Välj ämne…</option>
                <option value="offert">Offertförfrågan</option>
                <option value="radgivning">Rådgivning om produkter</option>
                <option value="provkollektion">Boka provkollektion</option>
                <option value="ovrigt">Övrigt</option>
              </select>
            </div>

            <div>
              <label htmlFor="meddelande" className="mb-1.5 block text-sm font-semibold text-stone-700">
                Meddelande <span className="text-red-500">*</span>
              </label>
              <textarea
                id="meddelande"
                name="meddelande"
                required
                rows={5}
                placeholder="Berätta om era behov, antal personer, önskade produkter eller övriga frågor…"
                className="w-full resize-none rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:bg-white focus:outline-none"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-full bg-stone-900 px-8 py-4 text-sm font-semibold uppercase tracking-widest text-white transition hover:bg-stone-700"
            >
              Skicka förfrågan
            </button>

            <p className="text-center text-xs text-stone-400">
              Vi svarar normalt inom 1–2 arbetsdagar.
            </p>
          </form>
        )}

        {/* Contact info */}
        <div className="mt-10 grid gap-6 sm:grid-cols-2 text-sm text-stone-600">
          <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
            <p className="font-semibold text-stone-900">Telefon &amp; e-post</p>
            <a href="tel:+46123456789" className="mt-2 block hover:text-stone-900">
              +46 12 345 67 89
            </a>
            <a href="mailto:info@uniforma.se" className="mt-1 block hover:text-stone-900">
              info@uniforma.se
            </a>
          </div>
          <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
            <p className="font-semibold text-stone-900">Kontor &amp; showroom</p>
            <p className="mt-2">Uniforma AB · Industrigatan 12</p>
            <p>123 45 Stockholm</p>
            <p className="mt-1 text-stone-400">Vardagar 08.00–17.00</p>
          </div>
        </div>

      </main>
    </div>
  );
}
