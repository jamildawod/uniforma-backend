import Link from "next/link";

import { fetchPublicProducts } from "@/lib/api/server";

export default async function ProductsPage() {
  const products = await fetchPublicProducts();

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
        <div className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {products.map((product) => (
            <Link key={product.id} className="rounded-[2rem] bg-white p-5 shadow-[0_18px_50px_rgba(16,35,63,0.08)]" href={`/products/${product.slug}`}>
              <div className="overflow-hidden rounded-[1.5rem] bg-[#e9eef5]">
                {product.image_url ? (
                  <img alt={product.name} className="h-64 w-full object-cover" src={product.image_url} />
                ) : (
                  <div className="flex h-64 items-center justify-center text-sm text-slate-500">Ingen bild tillgänglig</div>
                )}
              </div>
              <div className="mt-5">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">{product.brand?.name || "UNIFORMA"}</p>
                <h2 className="mt-2 text-2xl font-semibold text-[#10233f]">{product.name}</h2>
                <p className="mt-3 line-clamp-3 text-sm text-slate-600">{product.description || "Kontakta oss for offert och tryckalternativ."}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
