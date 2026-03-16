import { CategoryManager } from "@/components/admin/category-manager";
import { Panel } from "@/components/ui/panel";
import { fetchAdminCategories } from "@/lib/api/server";

export default async function AdminCategoriesPage() {
  const categories = await fetchAdminCategories();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Catalog</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Categories</h2>
        <p className="mt-2 text-sm text-slate-600">Create, update, and delete category records that drive storefront navigation and product grouping.</p>
      </Panel>
      <CategoryManager initialCategories={categories} />
    </div>
  );
}
