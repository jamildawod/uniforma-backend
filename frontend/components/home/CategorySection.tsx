"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { API_URL, API_ORIGIN } from "@/lib/api";

const gradientClasses = [
  "from-stone-900/70 via-stone-900/40 to-stone-800/20",
  "from-slate-900/70 via-slate-800/40 to-slate-700/10",
  "from-amber-900/70 via-orange-900/50 to-stone-700/10",
  "from-cyan-900/70 via-slate-800/40 to-stone-600/10",
];

// Hero images for the 6 sector categories (served by Next.js /public)
const SECTOR_HERO_IMAGES: Record<string, string> = {
  dental: "/hero-dental.png",
  djursjukvard: "/hero-djursjukvard.png",
  "vard-omsorg": "/hero-vard.png",
  "stad-service": "/hero-stad.png",
  kok: "/hero-kok.png",
  "skonhet-halsa": "/hero-skonhet.png",
};

// Desired display order for the 6 main sector categories
const MAIN_CATEGORY_ORDER = [
  "dental",
  "djursjukvard",
  "skonhet-halsa",
  "vard-omsorg",
  "stad-service",
  "kok",
];

type Category = {
  id: number;
  name: string;
  slug?: string | null;
  image?: string | null;
  product_count?: number | null;
  parent_id?: number | null;
};

type Props = {
  title?: string;
  href?: string;
};

function toSlug(name: string) {
  return name
    .toLowerCase()
    .replace(/å/g, "a")
    .replace(/ä/g, "a")
    .replace(/ö/g, "o")
    .replace(/\s+/g, "-");
}

function resolveImageUrl(image?: string | null): string | null {
  if (!image) return null;
  try {
    // If it's already a full URL, return as-is
    new URL(image);
    return image;
  } catch {
    // Root-relative path like /uploads/foo.jpg — attach to API origin
    return `${API_ORIGIN}${image}`;
  }
}

function CategoryCard({
  category,
  index,
}: {
  category: Category;
  index: number;
}) {
  const slug = category.slug || toSlug(category.name);
  const heroImage = SECTOR_HERO_IMAGES[slug] ?? null;
  const imageUrl = resolveImageUrl(category.image) ?? heroImage;
  const [imgError, setImgError] = useState(false);
  const effectiveImageUrl = imgError ? null : imageUrl;

  return (
    <Link
      href={`/shop?category=${encodeURIComponent(slug)}`}
      className="relative h-[260px] rounded-2xl overflow-hidden group block"
    >
      {effectiveImageUrl ? (
        <img
          src={effectiveImageUrl}
          alt={category.name}
          className="absolute inset-0 w-full h-full object-cover"
          onError={() => setImgError(true)}
        />
      ) : (
        <div className="absolute inset-0 bg-stone-700" />
      )}
      <div className="absolute inset-0 bg-black/40 group-hover:bg-black/55 transition-colors duration-200" />
      <div className="absolute inset-0 flex items-center justify-center">
        <h2 className="text-white text-2xl font-semibold drop-shadow-md text-center px-4">
          {category.name}
        </h2>
      </div>
    </Link>
  );
}

export function CategorySection({
  title = "Kategorier",
  href = "/shop",
}: Props) {
  const [fetchedCategories, setFetchedCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isActive = true;

    async function loadCategories() {
      try {
        const response = await fetch(`${API_URL}/categories`);
        if (!response.ok) throw new Error("Category fetch failed");
        const payload = await response.json();
        const list: Category[] = Array.isArray(payload)
          ? payload
          : Array.isArray(payload?.data)
            ? payload.data
            : [];
        if (isActive) {
          setFetchedCategories(list);
        }
      } catch {
        if (isActive) {
          setFetchedCategories([]);
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    loadCategories();

    return () => {
      isActive = false;
    };
  }, []);

  const mainCategories = fetchedCategories.filter((cat) => !cat.parent_id);
  const unsorted = mainCategories.length > 0 ? mainCategories : fetchedCategories;
  const categoriesToRender = [...unsorted].sort((a, b) => {
    const slugA = a.slug || toSlug(a.name);
    const slugB = b.slug || toSlug(b.name);
    const iA = MAIN_CATEGORY_ORDER.indexOf(slugA);
    const iB = MAIN_CATEGORY_ORDER.indexOf(slugB);
    const posA = iA === -1 ? Infinity : iA;
    const posB = iB === -1 ? Infinity : iB;
    return posA - posB;
  });

  const showPlaceholder = loading;
  const hasCategories = fetchedCategories.length > 0;
  const showEmptyState = !loading && !hasCategories;

  return (
    <section className="mx-auto max-w-6xl px-4 py-12 md:py-16">
      <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.5em] text-stone-400">
            Utforska
          </p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-stone-950">
            {title}
          </h2>
        </div>
        <Link
          href={href}
          className="inline-flex items-center gap-1 text-sm font-semibold text-stone-500 transition hover:text-stone-950"
        >
          Visa alla
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {showEmptyState ? (
          <div className="col-span-full rounded-xl border border-gray-200 bg-stone-50 px-6 py-12 text-center text-sm font-semibold text-stone-600 shadow-sm">
            Inga kategorier hittades
          </div>
        ) : showPlaceholder ? (
          Array.from({ length: 6 }).map((_, index) => (
            <div
              key={`placeholder-${index}`}
              className="h-[260px] rounded-2xl bg-stone-200 animate-pulse"
            />
          ))
        ) : (
          categoriesToRender.map((category, index) => (
            <CategoryCard key={category.id} category={category} index={index} />
          ))
        )}
      </div>
    </section>
  );
}
