import { notFound } from "next/navigation";

import { QuoteForm } from "@/components/public/quote-form";
import { fetchPublicProduct } from "@/lib/api/server";

export default async function ProductDetailPage({
  params
}: {
  params: { slug: string };
}) {
  const product = await fetchPublicProduct(params.slug);
  if (!product) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      <div className="mx-auto grid max-w-7xl gap-10 px-6 py-16 lg:grid-cols-[1.1fr_0.9fr] lg:px-8">
        <div className="space-y-6">
          <div className="overflow-hidden rounded-[2rem] bg-white shadow-[0_18px_50px_rgba(16,35,63,0.08)]">
            {product.image_url ? (
              <img alt={product.name} className="h-[28rem] w-full object-cover" src={product.image_url} />
            ) : (
              <div className="flex h-[28rem] items-center justify-center text-sm text-slate-500">Ingen produktbild</div>
            )}
          </div>
          <div className="rounded-[2rem] bg-white p-8 shadow-[0_18px_50px_rgba(16,35,63,0.08)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#f28b39]">{product.brand?.name || "UNIFORMA"}</p>
            <h1 className="mt-3 text-4xl font-semibold text-[#10233f]">{product.name}</h1>
            <p className="mt-5 text-base leading-8 text-slate-600">
              {product.description || "Kontakta oss sa tar vi fram forslag pa modell, tryck och leveransupplagg."}
            </p>
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
    </main>
  );
}
