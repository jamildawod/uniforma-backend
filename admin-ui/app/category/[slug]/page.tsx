import { ProductGrid } from "@/components/catalog/ProductGrid";
import { fetchCatalogCategories, fetchPublicProducts } from "@/lib/api/server";

export default async function CategoryPage({ params }: { params: { slug: string } }) {
  const categories = await fetchCatalogCategories();
  const selected = categories.find((item) => item.slug === params.slug);
  const catalog = await fetchPublicProducts({ category: selected?.name });

  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#f28b39]">Kategori</p>
          <h1 className="mt-2 text-4xl font-semibold text-[#10233f]">{selected?.name ?? "Produkter"}</h1>
        </div>
        <div className="mt-10">
          <ProductGrid initialCatalog={catalog} categories={categories || []} />
        </div>
      </div>
    </main>
  );
}
