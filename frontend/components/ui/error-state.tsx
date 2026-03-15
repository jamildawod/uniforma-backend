export function ErrorState({
  title,
  message
}: {
  title: string;
  message: string;
}) {
  return (
    <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 text-rose-800">
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mt-1 text-sm">{message}</p>
    </div>
  );
}
