"use client";

import { startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { FilterSidebar } from "@/components/catalog/FilterSidebar";
import { ProductCard } from "@/components/catalog/ProductCard";
import { ProductCardSkeleton } from "@/components/catalog/ProductCardSkeleton";
import { MegaMenu } from "@/components/navigation/MegaMenu";
import { SearchBar } from "@/components/search/SearchBar";
import { InfiniteScroll } from "@/components/ui/InfiniteScroll";
import { getCatalogProducts } from "@/lib/api/client";
import type { CatalogProductList, CatalogProductSummary, CategoryTreeNode } from "@/lib/types/products";

type QueryState = {
  category: string[];
  brand: string[];
  color: string[];
  size: string[];
  price?: string;
  search?: string;
};

function matchesPrice(product: CatalogProductSummary, price?: string) {
  if (!price || !product.price) {
    return true;
  }
  const numeric = Number(product.price);
  if (Number.isNaN(numeric)) {
    return true;
  }
  if (price === "0-300") return numeric < 300;
  if (price === "300-600") return numeric >= 300 && numeric < 600;
  if (price === "600+") return numeric >= 600;
  return true;
}

export function ProductGrid({
  initialCatalog,
  categories,
  initialQuery
}: {
  initialCatalog: CatalogProductList;
  categories: CategoryTreeNode[];
  initialQuery: QueryState;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [products, setProducts] = useState(initialCatalog.products);
  const [nextCursor, setNextCursor] = useState<string | null>(initialCatalog.next_cursor);
  const [filters, setFilters] = useState(initialCatalog.filters);
  const [query, setQuery] = useState<QueryState>(initialQuery);
  const [searchValue, setSearchValue] = useState(initialQuery.search ?? "");
  const [loading, setLoading] = useState(false);
  const deferredSearchValue = useDeferredValue(searchValue);

  useEffect(() => {
    const handle = setTimeout(async () => {
      setLoading(true);
      const response = await getCatalogProducts({
        category: query.category,
        brand: query.brand,
        color: query.color,
        size: query.size,
        search: deferredSearchValue || undefined,
        limit: 24
      });
      startTransition(() => {
        setProducts(response.products);
        setNextCursor(response.next_cursor);
        setFilters(response.filters);
        setQuery((current) => ({ ...current, search: deferredSearchValue || undefined }));
      });
      setLoading(false);
    }, 300);

    return () => clearTimeout(handle);
  }, [deferredSearchValue, query.brand, query.category, query.color, query.size]);

  useEffect(() => {
    const params = new URLSearchParams();
    for (const value of query.category) params.append("category", value);
    for (const value of query.brand) params.append("brand", value);
    for (const value of query.color) params.append("color", value);
    for (const value of query.size) params.append("size", value);
    if (query.price) params.set("price", query.price);
    if (deferredSearchValue) params.set("search", deferredSearchValue);
    router.replace(params.size ? `${pathname}?${params.toString()}` : pathname, { scroll: false });
  }, [deferredSearchValue, pathname, query.brand, query.category, query.color, query.price, query.size, router]);

  const visibleProducts = useMemo(
    () => products.filter((product) => matchesPrice(product, query.price)),
    [products, query.price]
  );

  const loadMore = async () => {
    if (!nextCursor || loading) {
      return;
    }
    setLoading(true);
    const response = await getCatalogProducts({
      category: query.category,
      brand: query.brand,
      color: query.color,
      size: query.size,
      search: query.search,
      cursor: nextCursor,
      limit: 24
    });
    startTransition(() => {
      setProducts((current) => [...current, ...response.products]);
      setNextCursor(response.next_cursor);
      setFilters(response.filters);
    });
    setLoading(false);
  };

  return (
    <div className="space-y-8">
      <div className="sticky top-0 z-20 space-y-4 bg-[#f5f7fb]/95 pb-2 pt-2 backdrop-blur">
        <SearchBar value={searchValue} onChange={setSearchValue} />
        <MegaMenu categories={categories} />
      </div>
      <div className="flex flex-col gap-6 lg:flex-row">
        <FilterSidebar
          categories={filters.categories}
          brands={filters.brands}
          colors={filters.colors}
          sizes={filters.sizes}
          value={query}
          onChange={setQuery}
        />
        <div className="flex-1">
          <div className="grid grid-cols-2 gap-6 md:grid-cols-3 lg:grid-cols-4">
            {visibleProducts.map((product) => (
              <ProductCard key={`${product.product_id}-${product.created_at}`} product={product} />
            ))}
            {loading
              ? Array.from({ length: 4 }).map((_, index) => <ProductCardSkeleton key={`loading-${index}`} />)
              : null}
          </div>
          {!visibleProducts.length && !loading ? (
            <div className="rounded-[1.75rem] border border-dashed border-slate-300 bg-white px-6 py-12 text-center text-sm text-slate-500">
              Inga produkter matchar dina filter just nu.
            </div>
          ) : null}
          <InfiniteScroll disabled={!nextCursor} loading={loading} onLoadMore={loadMore} />
        </div>
      </div>
    </div>
  );
}
