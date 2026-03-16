"use client";

export default function GlobalError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-100 text-slate-950">
        <main className="mx-auto flex min-h-screen max-w-3xl items-center px-6 py-10">
          <div className="w-full rounded-3xl border border-rose-200 bg-white p-8 shadow-panel">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-rose-700">Application Error</p>
            <h1 className="mt-2 text-3xl font-semibold text-ink">The interface hit a fatal error.</h1>
            <p className="mt-3 text-sm text-slate-600">{error.message || "Unexpected application error."}</p>
            <button
              className="mt-6 rounded-2xl bg-ink px-4 py-3 text-sm font-semibold text-white"
              onClick={() => reset()}
              type="button"
            >
              Retry
            </button>
          </div>
        </main>
      </body>
    </html>
  );
}
