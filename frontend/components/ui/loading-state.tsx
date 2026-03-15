export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <div className="rounded-3xl bg-white/80 p-6 shadow-panel">
      <div className="h-4 w-28 animate-pulse rounded bg-slate-200" />
      <p className="mt-3 text-sm text-slate-500">{label}...</p>
    </div>
  );
}
