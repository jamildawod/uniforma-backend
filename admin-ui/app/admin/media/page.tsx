import { Panel } from "@/components/ui/panel";
import { fetchAdminMedia } from "@/lib/api/server";

export default async function AdminMediaPage() {
  const media = await fetchAdminMedia();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">PIM</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Media Library</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {media.map((item) => (
            <div key={item.filename} className="overflow-hidden rounded-2xl border border-slate-200 bg-slate-50">
              <img alt={item.filename} className="h-48 w-full object-cover" src={item.url} />
              <div className="p-4">
                <p className="truncate text-sm font-medium text-ink">{item.filename}</p>
              </div>
            </div>
          ))}
          {media.length === 0 ? <p className="text-sm text-slate-500">No media uploaded yet.</p> : null}
        </div>
      </Panel>
    </div>
  );
}
