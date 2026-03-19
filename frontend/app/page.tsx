import { CategorySection } from "@/components/home/CategorySection";
import { CategoryProductsRow } from "@/components/home/CategoryProductsRow";
import { fetchFilters } from "@/lib/api";

export default async function HomePage() {
  // Use /filters categories — these are the garment-type categories that have actual products
  const filters = await fetchFilters();
  const featuredCategories = filters.categories.slice(0, 4);

  return (
    <div className="overflow-hidden">
      <CategorySection />
      <div className="border-t border-stone-100 pt-4">
        {featuredCategories.map((category) => (
          <CategoryProductsRow key={category.id} category={category} />
        ))}
      </div>
    </div>
  );
}
