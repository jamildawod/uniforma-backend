"use client";

export default function AdminError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 text-rose-950 shadow-panel">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-rose-700">Admin Error</p>
      <h2 className="mt-2 text-2xl font-semibold">Something failed while rendering this admin page.</h2>
      <p className="mt-3 text-sm text-rose-900/80">{error.message || "Unexpected application error."}</p>
      <button
        className="mt-4 rounded-2xl bg-rose-700 px-4 py-3 text-sm font-semibold text-white"
        onClick={() => reset()}
        type="button"
      >
        Retry
      </button>
    </div>
  );
}
