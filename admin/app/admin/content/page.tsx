import { ContentEditor } from "@/components/admin/content-editor";
import { Panel } from "@/components/ui/panel";
import { fetchAdminContent } from "@/lib/api/server";

export default async function AdminContentPage() {
  const content = await fetchAdminContent();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Content</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Homepage and company content</h2>
        <p className="mt-2 text-sm text-slate-600">Edit hero text, featured homepage categories, company copy, and contact messaging.</p>
      </Panel>
      {content ? <ContentEditor initial={content} /> : null}
    </div>
  );
}
