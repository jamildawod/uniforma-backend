import { Suspense } from "react";
import { ArrowLeft, ArrowRight, LayoutGrid } from "lucide-react";
import { FilterSidebar } from "@/components/FilterSidebar";
import { ProductCard, type StoreProduct } from "@/components/ProductCard";
import { normalizeSize } from "@/lib/size-filter";
import { API_URL } from "@/lib/api";

type FilterData = {
  colors: string[];
  sizes: string[];
  categories: Array<{
    id: number;
    name: string;
    slug: string;
    parent_id: number | null;
  }>;
};

type ShopPageProps = {
  searchParams?: {
    category?: string;
    size?: string;
    color?: string;
    page?: string;
  };
};

const PAGE_SIZE = 48;

async function getFilters(): Promise<FilterData> {
  try {
    const response = await fetch(`${API_URL}/filters`, {
      next: { revalidate: 300 },
    });
    if (!response.ok) return { colors: [], sizes: [], categories: [] };
    const payload = await response.json();

    return {
      colors: Array.isArray(payload?.colors) ? payload.colors : [],
      sizes: Array.isArray(payload?.sizes) ? payload.sizes : [],
      categories: Array.isArray(payload?.categories) ? payload.categories : [],
    };
  } catch {
    return { colors: [], sizes: [], categories: [] };
  }
}

async function getProducts(params: {
  category?: string;
  size?: string;
  color?: string;
  page: number;
}): Promise<StoreProduct[]> {
  try {
    const query = new URLSearchParams();
    query.set("limit", String(PAGE_SIZE));
    query.set("offset", String((params.page - 1) * PAGE_SIZE));
    if (params.category) query.set("category", params.category);
    if (params.size) query.set("size", params.size);
    if (params.color) query.set("color", params.color);

    const response = await fetch(
      `${API_URL}/products?${query.toString()}`,
      { next: { revalidate: 60 } },
    );
    if (!response.ok) return [];
    const payload = await response.json();
    return Array.isArray(payload)
      ? payload
      : Array.isArray(payload?.data)
        ? payload.data
        : [];
  } catch {
    return [];
  }
}

export default async function ShopPage({ searchParams }: ShopPageProps) {
  const selectedCategory = searchParams?.category ?? "";
  const rawSizeParam = searchParams?.size ?? "";
  const rawColorParam = searchParams?.color ?? "";
  const selectedSize = normalizeSize(rawSizeParam) ?? "";
  const selectedColor = rawColorParam.trim();
  const page = Math.max(1, parseInt(searchParams?.page ?? "1", 10));

  const [filters, products] = await Promise.all([
    getFilters(),
    getProducts({
      category: selectedCategory || undefined,
      size: selectedSize || undefined,
      color: selectedColor || undefined,
      page,
    }),
  ]);

  const safeCategories = filters.categories ?? [];
  const safeColors = filters.colors ?? [];
  const safeProducts = products ?? [];

  // Normalize sizes from filters endpoint; fall back to ALLOWED_SIZES ordering
  const uniqueSizes = (filters.sizes ?? [])
    .map((s) => normalizeSize(s))
    .filter((s): s is string => s !== null)
    .filter((s, i, arr) => arr.indexOf(s) === i);

  const hasFilters = !!(selectedCategory || selectedSize || selectedColor);
  const activeCategoryName = selectedCategory
    ? safeCategories.find((c) => c.slug === selectedCategory)?.name
    : null;

  return (
    <div className="min-h-screen bg-stone-50 text-stone-950">
      {/* Page header */}
      <div className="border-b border-stone-200 bg-white">
        <div className="mx-auto max-w-[1440px] px-6 py-8 lg:px-10 xl:px-12">
          <p className="text-xs font-semibold uppercase tracking-widest text-stone-400">
            {hasFilters ? "Filtrerad katalog" : "Produktkatalog"}
          </p>
          <h1 className="mt-1.5 text-3xl font-bold tracking-tight text-stone-950 sm:text-4xl">
            {activeCategoryName ?? "Alla produkter"}
          </h1>
          {!hasFilters && (
            <p className="mt-3 max-w-2xl text-sm text-stone-500">
              Uniformas katalog med arbetskläder och relaterade produkter för
              professionella miljöer.
            </p>
          )}
        </div>
      </div>

      <main className="mx-auto max-w-[1440px] px-6 py-8 lg:px-10 xl:px-12">
        <div className="grid gap-8 lg:grid-cols-[260px_1fr] xl:grid-cols-[280px_1fr]">
          {/* Sidebar */}
          <Suspense fallback={null}>
            <FilterSidebar
              categories={safeCategories}
              uniqueSizes={uniqueSizes}
              colors={safeColors}
              selectedCategory={selectedCategory}
              selectedSize={selectedSize}
              selectedColor={selectedColor}
            />
          </Suspense>

          {/* Product grid */}
          <div>
            {/* Toolbar */}
            <div className="mb-5 flex items-center justify-between gap-3 rounded-xl border border-stone-200 bg-white px-4 py-3 shadow-sm">
              <div className="flex items-center gap-2 text-sm text-stone-600">
                <LayoutGrid className="h-4 w-4 text-stone-400" />
                <span>
                  <span className="font-semibold text-stone-950">
                    {safeProducts.length}
                  </span>{" "}
                  {safeProducts.length === 1 ? "produkt" : "produkter"}
                  {page > 1 && (
                    <span className="text-stone-400"> · sida {page}</span>
                  )}
                </span>
              </div>
              {hasFilters && (
                <span className="rounded-full bg-stone-100 px-3 py-1 text-xs font-medium text-stone-600">
                  Filter aktivt
                </span>
              )}
            </div>

            {/* Grid */}
            {safeProducts.length > 0 ? (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
                {safeProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-stone-300 bg-white px-8 py-20 text-center">
                <LayoutGrid className="mx-auto mb-4 h-10 w-10 text-stone-300" />
                <h2 className="text-lg font-semibold text-stone-950">
                  {hasFilters
                    ? "Inga produkter matchade ditt filter"
                    : "Inga produkter hittades"}
                </h2>
                <p className="mt-2 text-sm text-stone-500">
                  {hasFilters
                    ? "Prova att justera eller ta bort filter för att se fler resultat."
                    : "Prova att justera dina filter för att se fler resultat."}
                </p>
              </div>
            )}

            {/* Pagination */}
            {(safeProducts.length === PAGE_SIZE || page > 1) && (
              <div className="mt-10 flex items-center justify-center gap-3">
                {page > 1 && (
                  <a
                    href={buildPageUrl(searchParams, page - 1)}
                    className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-5 py-2.5 text-sm font-medium text-stone-700 shadow-sm transition hover:border-stone-300 hover:bg-stone-50"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    Föregående
                  </a>
                )}
                <span className="rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-medium text-stone-500 shadow-sm">
                  Sida {page}
                </span>
                {safeProducts.length === PAGE_SIZE && (
                  <a
                    href={buildPageUrl(searchParams, page + 1)}
                    className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-5 py-2.5 text-sm font-medium text-stone-700 shadow-sm transition hover:border-stone-300 hover:bg-stone-50"
                  >
                    Nästa
                    <ArrowRight className="h-4 w-4" />
                  </a>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function buildPageUrl(
  searchParams: ShopPageProps["searchParams"],
  page: number,
): string {
  const params = new URLSearchParams();
  if (searchParams?.category) params.set("category", searchParams.category);
  if (searchParams?.size) params.set("size", searchParams.size);
  if (searchParams?.color) params.set("color", searchParams.color);
  if (page > 1) params.set("page", String(page));
  const qs = params.toString();
  return qs ? `/shop?${qs}` : "/shop";
}
