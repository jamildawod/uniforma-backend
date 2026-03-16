import Image from "next/image";
import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ProductCard } from "@/components/catalog/ProductCard";
import { ProductGallery } from "@/components/public/ProductGallery";
import { QuoteForm } from "@/components/public/quote-form";
import { fetchPublicProduct, fetchPublicProducts } from "@/lib/api/server";

export const revalidate = 300;

export async function generateMetadata({
  params
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const product = await fetchPublicProduct(params.slug);
  if (!product) {
    return {
      title: "Produkt | Uniforma",
      description: "Produktinformation från Uniforma."
    };
  }

  return {
    title: `${product.name} | Uniforma`,
    description: product.description || `Upptäck ${product.name} hos Uniforma.`,
    openGraph: {
      title: `${product.name} | Uniforma`,
      description: product.description || `Upptäck ${product.name} hos Uniforma.`,
      images: product.image_url ? [{ url: product.image_url }] : undefined
    }
  };
}

export default async function ProductDetailPage({
  params
}: {
  params: { slug: string };
}) {
  const product = await fetchPublicProduct(params.slug);
  if (!product) {
    notFound();
  }
  const relatedCatalog = await fetchPublicProducts({ category: product.category?.name, limit: 8 });
  const relatedProducts = relatedCatalog.products.filter((item) => item.slug !== product.slug).slice(0, 8);
  const galleryImages =
    product.images.length > 0
      ? product.images.map((image) => ({ id: image.id, url: image.url || "/images/placeholder.webp", alt: product.name }))
      : [{ id: "fallback", url: product.image_url || "/images/placeholder.webp", alt: product.name }];
  const availableSizes = Array.from(new Set(product.variants.map((variant) => variant.size).filter(Boolean))) as string[];
  const availableColors = Array.from(new Set(product.variants.map((variant) => variant.color).filter(Boolean))) as string[];

  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      <div className="mx-auto grid max-w-7xl gap-10 px-6 py-16 pb-28 lg:grid-cols-[1.1fr_0.9fr] lg:px-8 lg:pb-16">
        <div className="space-y-6">
          <ProductGallery images={galleryImages} fallbackAlt={product.name} />
          <div className="rounded-[2rem] bg-white p-8 shadow-[0_18px_50px_rgba(16,35,63,0.08)]">
            <div className="flex flex-wrap items-center gap-4">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#f28b39]">{product.brand?.name || "UNIFORMA"}</p>
              {product.brand?.logo_url ? (
                <Image
                  src={product.brand.logo_url}
                  alt={product.brand.name}
                  width={120}
                  height={40}
                  sizes="120px"
                  className="h-8 w-auto object-contain"
                />
              ) : null}
            </div>
            <h1 className="mt-3 text-4xl font-semibold text-[#10233f]">{product.name}</h1>
            <p className="mt-5 text-base leading-8 text-slate-600">
              {product.description || "Kontakta oss sa tar vi fram forslag pa modell, tryck och leveransupplagg."}
            </p>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Storlekar</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {availableSizes.length ? availableSizes.map((size) => <span key={size} className="rounded-full bg-white px-3 py-2 text-sm text-[#10233f]">{size}</span>) : <span className="text-sm text-slate-500">Kontakta oss</span>}
                </div>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Färger</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {availableColors.length ? availableColors.map((color) => <span key={color} className="rounded-full bg-white px-3 py-2 text-sm text-[#10233f]">{color}</span>) : <span className="text-sm text-slate-500">Kontakta oss</span>}
                </div>
              </div>
            </div>
            {product.variants.length > 0 ? (
              <div className="mt-6 grid gap-3 md:grid-cols-2">
                {product.variants.map((variant) => (
                  <div key={variant.id} className="rounded-2xl border border-slate-200 p-4">
                    <p className="font-medium text-[#10233f]">{variant.sku}</p>
                    <p className="text-sm text-slate-500">
                      {variant.color || "Standard"} / {variant.size || "One size"} / Lager {variant.stock_quantity}
                    </p>
                  </div>
                ))}
              </div>
            ) : null}
            <a className="mt-8 inline-flex rounded-full bg-[#f28b39] px-6 py-3 text-sm font-semibold text-white" href="#product-quote">
              Begär offert
            </a>
          </div>
        </div>

        <div id="product-quote">
          <QuoteForm
            compact
            defaultMessage={`Hej, jag vill ha offert pa ${product.name}. Vi vill veta mer om priser, tryck och leverans.`}
            productId={product.id}
            variantId={product.variants[0]?.id}
            title={`Offert for ${product.name}`}
          />
        </div>
      </div>
      {relatedProducts.length > 0 ? (
        <section className="mx-auto max-w-7xl px-6 pb-24 lg:px-8">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#f28b39]">Relaterat</p>
              <h2 className="mt-2 text-3xl font-semibold text-[#10233f]">Fler produkter i samma kategori</h2>
            </div>
          </div>
          <div className="mt-8 grid grid-cols-2 gap-6 md:grid-cols-3 lg:grid-cols-4">
            {relatedProducts.map((related) => (
              <ProductCard key={related.product_id} product={related} />
            ))}
          </div>
        </section>
      ) : null}
      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-slate-200 bg-white/95 p-4 backdrop-blur lg:hidden">
        <a className="flex w-full items-center justify-center rounded-full bg-[#f28b39] px-6 py-4 text-sm font-semibold text-white" href="#product-quote">
          Begär offert
        </a>
      </div>
    </main>
  );
}
