import { cn } from "@/lib/utils/cn";

export function Panel({
  className,
  children
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return <section className={cn("rounded-3xl bg-white/90 p-6 shadow-panel backdrop-blur", className)}>{children}</section>;
}
