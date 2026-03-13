import { ProductEditor } from "@/components/admin/product-editor";
import { Panel } from "@/components/ui/panel";
import { fetchAdminAttributes, fetchAdminBrands, fetchAdminCategories } from "@/lib/api/server";

export default async function AdminNewProductPage() {
  const [brands, categories, attributes] = await Promise.all([
    fetchAdminBrands(),
    fetchAdminCategories(),
    fetchAdminAttributes()
  ]);
  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Catalog</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Create Product</h2>
        <div className="mt-6">
          <ProductEditor attributes={attributes} brands={brands} categories={categories} mode="create" />
        </div>
      </Panel>
    </div>
  );
}
