import Link from "next/link";
import type { Metadata } from "next";

import { ProductGrid } from "@/components/catalog/ProductGrid";
import { fetchCatalogCategories, fetchPublicProducts } from "@/lib/api/server";

export const metadata: Metadata = {
  title: "Uniformer och arbetskläder | Uniforma",
  description: "Utforska Uniformas katalog med arbetskläder, profilplagg och företagsuniformer.",
  openGraph: {
    title: "Uniformer och arbetskläder | Uniforma",
    description: "Utforska Uniformas katalog med arbetskläder, profilplagg och företagsuniformer."
  }
};

export const revalidate = 60;

function normalizeMultiValue(value: string | string[] | undefined): string[] {
  if (!value) return [];
  return (Array.isArray(value) ? value : [value]).flatMap((entry) => entry.split(",")).map((entry) => entry.trim()).filter(Boolean);
}

export default async function ProductsPage({
  searchParams
}: {
  searchParams?: Record<string, string | string[] | undefined>;
}) {
  const initialQuery = {
    category: normalizeMultiValue(searchParams?.category),
    brand: normalizeMultiValue(searchParams?.brand),
    color: normalizeMultiValue(searchParams?.color),
    size: normalizeMultiValue(searchParams?.size),
    price: typeof searchParams?.price === "string" ? searchParams.price : undefined,
    search: typeof searchParams?.search === "string" ? searchParams.search : undefined
  };
  const catalog = await fetchPublicProducts({
    category: initialQuery.category,
    brand: initialQuery.brand,
    color: initialQuery.color,
    size: initialQuery.size,
    search: initialQuery.search,
    limit: 24
  });
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
          <ProductGrid initialCatalog={catalog} categories={categories || []} initialQuery={initialQuery} />
        </div>
      </div>
    </main>
  );
}
