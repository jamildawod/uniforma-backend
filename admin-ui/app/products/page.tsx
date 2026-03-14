import Link from "next/link";

import { ProductGrid } from "@/components/catalog/ProductGrid";
import { fetchCatalogCategories, fetchPublicProducts } from "@/lib/api/server";

export default async function ProductsPage() {
  const catalog = await fetchPublicProducts();
  const categories = await fetchCatalogCategories();

  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#f28b39]">Katalog</p>
            <h1 className="mt-2 text-4xl font-semibold text-[#10233f]">Produkter för profilering och tryck</h1>
          </div>
          <Link className="rounded-full bg-[#10233f] px-5 py-3 text-sm font-semibold text-white" href="/#quote-form">
            Begär offert
          </Link>
        </div>
        <div className="mt-10">
          <ProductGrid initialCatalog={catalog} categories={categories} />
        </div>
      </div>
    </main>
  );
}
