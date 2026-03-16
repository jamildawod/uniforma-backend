import { MediaLibraryManager } from "@/components/admin/media-library-manager";
import { Panel } from "@/components/ui/panel";
import { fetchAdminMedia } from "@/lib/api/server";

export default async function AdminMediaPage() {
  const media = await fetchAdminMedia();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Media</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Image library</h2>
        <p className="mt-2 text-sm text-slate-600">Upload, review, and delete uploaded media assets used by product records.</p>
      </Panel>
      <MediaLibraryManager initialMedia={media} />
    </div>
  );
}
