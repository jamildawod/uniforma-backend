export function ProductCardSkeleton() {
  return (
    <div className="animate-pulse rounded-[1.75rem] border border-slate-200 bg-white p-4 shadow-[0_18px_50px_rgba(16,35,63,0.08)]">
      <div className="h-56 rounded-[1.25rem] bg-slate-200" />
      <div className="mt-4 h-3 w-28 rounded-full bg-slate-200" />
      <div className="mt-3 h-6 w-4/5 rounded-full bg-slate-200" />
      <div className="mt-3 h-4 w-1/3 rounded-full bg-slate-100" />
      <div className="mt-4 flex gap-2">
        <div className="h-7 w-16 rounded-full bg-slate-100" />
        <div className="h-7 w-16 rounded-full bg-slate-100" />
      </div>
    </div>
  );
}
