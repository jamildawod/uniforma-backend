"use client";

import Image from "next/image";
import Link from "next/link";

import type { CatalogProductSummary } from "@/lib/types/products";

export function ProductCard({ product }: { product: CatalogProductSummary }) {
  const productName = product.name ?? "Produkt";
  const productCategory = product.category ?? product.brand ?? "Uniforma";

  return (
    <Link
      href={`/products/${product.slug}`}
      className="group flex h-full flex-col overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white shadow-[0_18px_50px_rgba(16,35,63,0.08)] transition-transform duration-200 hover:-translate-y-1"
    >
      <div className="relative overflow-hidden bg-[#edf2f7]">
        <Image
          src={product.primary_image || "/images/placeholder.webp"}
          alt={productName}
          width={500}
          height={500}
          sizes="(max-width:768px) 100vw, 25vw"
          loading="lazy"
          className="h-56 w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
        />
      </div>
      <div className="flex flex-1 flex-col p-4">
        <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">{productCategory}</p>
        <h3 className="mt-2 line-clamp-2 text-lg font-semibold text-[#10233f]">{productName}</h3>
        <p className="mt-3 text-sm font-medium text-[#10233f]">{product.price ? `${product.price} SEK` : "Pris vid offert"}</p>
        <p className="mt-4 text-sm text-slate-600">
          {product.colors?.length ? product.colors.slice(0, 3).join(", ") : "Kontakta oss för färgval."}
        </p>
      </div>
    </Link>
  );
}
