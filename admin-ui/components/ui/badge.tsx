import { cn } from "@/lib/utils/cn";

const variants = {
  neutral: "bg-slate-100 text-slate-700",
  success: "bg-emerald-100 text-emerald-700",
  warning: "bg-amber-100 text-amber-800",
  danger: "bg-rose-100 text-rose-700",
  info: "bg-sky-100 text-sky-700"
} as const;

export function Badge({
  variant = "neutral",
  children
}: {
  variant?: keyof typeof variants;
  children: React.ReactNode;
}) {
  return (
    <span className={cn("inline-flex rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.18em]", variants[variant])}>
      {children}
    </span>
  );
}
