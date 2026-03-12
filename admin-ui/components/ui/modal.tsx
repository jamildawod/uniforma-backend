"use client";

export function Modal({
  open,
  title,
  onClose,
  children
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/45 p-4">
      <div className="w-full max-w-xl rounded-3xl bg-white p-6 shadow-panel">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-ink">{title}</h3>
          <button className="text-sm text-slate-500 hover:text-ink" onClick={onClose} type="button">
            Close
          </button>
        </div>
        <div className="mt-4">{children}</div>
      </div>
    </div>
  );
}
