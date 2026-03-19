"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { API_ORIGIN } from "@/lib/api";

export type StoreImageLike = StoreImage | string;

export type StoreImage = {
  id: number;
  external_path: string;
  local_path: string | null;
  is_primary: boolean;
  sort_order: number;
  url?: string | null;
};

export type StoreVariant = {
  id: number;
  sku?: string;
  color: string | null;
  size: string | null;
  price: number | string | null;
  currency: string | null;
  stock_quantity?: number;
  is_active?: boolean;
  images: StoreImageLike[];
};

export type StoreCertification = {
  name: string;
  label: string | null;
  qr: string | null;
};

export type StoreProduct = {
  id: string;
  external_id?: string;
  name: string;
  slug: string;
  description: string | null;
  brand: string | null;
  material?: string | null;
  care_instructions?: string[];
  tags?: string[];
  certifications?: StoreCertification[];
  qr_code?: string | null;
  attributes?: Record<string, string>;
  price?: string | number | null;
  category: {
    id: number;
    name: string;
    slug: string;
    parent_id: number | null;
  } | null;
  images: StoreImageLike[];
  variants: StoreVariant[];
  category_slug?: string | null;
  colors?: string[];
  sizes?: string[];
};

/**
 * Convert any image path to an absolute URL suitable for <img src>.
 * Uses API_ORIGIN (not API_URL which includes /api/v1) so that root-relative
 * paths like /uploads/foo.jpg resolve correctly to the API host origin.
 */
export function toAbsoluteUrl(path?: string | null): string | null {
  if (!path) return null;
  // Fix mangled proxy paths like /media/http/... or /media/https/... → https://...
  const cleaned = path.replace(/^\/media\/https?\//, "https://");
  try {
    // If it's already a full URL (http/https), new URL() returns it unchanged.
    // For root-relative paths (/uploads/...) it strips the base path and uses
    // only the origin — which is exactly what we want.
    return new URL(cleaned, API_ORIGIN).toString();
  } catch {
    return null;
  }
}

function resolveImageCandidate(image?: StoreImageLike | null): string | null {
  if (!image) return null;
  if (typeof image === "string") {
    return toAbsoluteUrl(image);
  }

  return (
    toAbsoluteUrl(image.url) ??
    toAbsoluteUrl(image.external_path) ??
    toAbsoluteUrl(image.local_path)
  );
}

/**
 * Pick the best available image URL for a product.
 * Always returns a non-empty string (falls back to /placeholder.jpg).
 */
export function resolveProductImage(
  product: Pick<StoreProduct, "images" | "variants">,
): string {
  const safeImages = product.images ?? [];
  const safeVariants = product.variants ?? [];

  const directImage = resolveImageCandidate(safeImages[0]);
  if (directImage) {
    return directImage;
  }

  const sortedImages = [...safeImages]
    .filter((image): image is StoreImage => typeof image !== "string")
    .sort((a, b) => {
      if (a.is_primary && !b.is_primary) return -1;
      if (!a.is_primary && b.is_primary) return 1;
      return (a.sort_order ?? 0) - (b.sort_order ?? 0);
    });

  const variantImages = safeVariants.flatMap((variant) => variant.images ?? []);
  const candidates: StoreImageLike[] = [...sortedImages, ...variantImages];

  for (const img of candidates) {
    const url = resolveImageCandidate(img);
    if (url) return url;
  }

  return "/placeholder.jpg";
}

/** Resolve a single StoreImage to an absolute URL (for galleries). */
export function resolveImageUrl(img: StoreImageLike): string {
  return resolveImageCandidate(img) ?? "/placeholder.jpg";
}

export function ProductCard({ product }: { product: StoreProduct }) {
  const primarySrc = resolveProductImage(product);
  // Track image error so we can fall back to placeholder without crashing.
  const [imgSrc, setImgSrc] = useState(primarySrc);
  const safeName = product.name || "Uniforma";
  const safeCategoryName = product.category?.name || "Produkt";

  return (
    <Link
      href={`/product/${product.slug}`}
      className="group bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-all duration-200 flex flex-col text-center"
    >
      {/* IMAGE */}
      <div className="relative aspect-square mb-2 bg-[#f5f5f5]">
        <Image
          src={imgSrc}
          alt={safeName}
          fill
          unoptimized
          className="object-contain p-2"
          sizes="200px"
          loading="lazy"
          onError={() => setImgSrc("/placeholder.jpg")}
        />
      </div>

      {/* TEXT */}
      <p className="text-[10px] uppercase text-gray-400 mb-0.5">
        {safeCategoryName}
      </p>
      <h3 className="text-sm font-medium text-gray-900 line-clamp-2 leading-snug mb-3">
        {safeName}
      </h3>

      {/* BUTTON */}
      <div className="mt-auto flex justify-center">
        <span className="bg-blue-500 text-white text-xs px-3 py-1.5 rounded-md hover:bg-blue-600 transition">
          Läs mer
        </span>
      </div>
    </Link>
  );
}
