import { ProductFilterForm } from "@/components/admin/product-filter-form";
import { ProductTable } from "@/components/admin/product-table";
import { ErrorState } from "@/components/ui/error-state";
import { Panel } from "@/components/ui/panel";
import { fetchAdminProducts } from "@/lib/api/server";
import type { ProductListFilters } from "@/lib/types/products";

type PageProps = {
  searchParams: Record<string, string | string[] | undefined>;
};

export default async function AdminProductsPage({ searchParams }: PageProps) {
  const filters: ProductListFilters = {
    page: Number(searchParams.page ?? 1),
    pageSize: 20,
    filter: typeof searchParams.filter === "string" ? searchParams.filter : undefined,
    search: typeof searchParams.search === "string" ? searchParams.search : undefined,
    isActive: typeof searchParams.isActive === "string" ? (searchParams.isActive as ProductListFilters["isActive"]) : "all",
    deleted: typeof searchParams.deleted === "string" ? (searchParams.deleted as ProductListFilters["deleted"]) : "all",
    hasOverride: typeof searchParams.hasOverride === "string" ? (searchParams.hasOverride as ProductListFilters["hasOverride"]) : "all"
  };

  try {
    const products = await fetchAdminProducts(filters);

    return (
      <div className="space-y-6">
        <Panel>
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Catalog</p>
              <h2 className="mt-1 text-2xl font-semibold text-ink">Products</h2>
            </div>
          </div>
          <div className="mt-6">
            <ProductFilterForm />
          </div>
        </Panel>
        <ProductTable filters={filters} products={products} />
      </div>
    );
  } catch (error) {
    return <ErrorState message={error instanceof Error ? error.message : "Unknown error"} title="Failed to load products" />;
  }
}
