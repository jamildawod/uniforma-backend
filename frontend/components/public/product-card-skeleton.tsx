export function ProductCardSkeleton() {
  return (
    <div className="animate-pulse rounded-[2rem] bg-white p-5 shadow-[0_18px_50px_rgba(16,35,63,0.08)]">
      <div className="h-64 rounded-[1.5rem] bg-slate-200" />
      <div className="mt-5">
        <div className="h-3 w-24 rounded-full bg-slate-200" />
        <div className="mt-3 h-8 w-3/4 rounded-full bg-slate-200" />
        <div className="mt-4 h-4 w-1/2 rounded-full bg-slate-100" />
      </div>
    </div>
  );
}
