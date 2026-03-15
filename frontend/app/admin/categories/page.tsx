import { Panel } from "@/components/ui/panel";
import { fetchAdminCategories } from "@/lib/api/server";

export default async function AdminCategoriesPage() {
  const categories = await fetchAdminCategories();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">PIM</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Categories</h2>
        <div className="mt-6 space-y-3">
          {categories.map((category) => (
            <div key={category.id} className="rounded-2xl border border-slate-200 p-4">
              <p className="font-semibold text-ink">{category.name}</p>
              <p className="text-sm text-slate-500">
                {category.slug} · position {category.position}
              </p>
            </div>
          ))}
          {categories.length === 0 ? <p className="text-sm text-slate-500">No categories available.</p> : null}
        </div>
      </Panel>
    </div>
  );
}
