import { ProductCardSkeleton } from "@/components/catalog/ProductCardSkeleton";

export default function ProductsLoading() {
  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="mt-10 grid grid-cols-2 gap-6 md:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 6 }).map((_, index) => (
            <ProductCardSkeleton key={index} />
          ))}
        </div>
      </div>
    </main>
  );
}
