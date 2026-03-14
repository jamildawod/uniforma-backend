import Image from "next/image";
import Link from "next/link";

import { QuoteForm } from "@/components/public/quote-form";
import { fetchPublicProducts } from "@/lib/api/server";

const services = [
  "Arbetskläder för team i butik, lager och fält",
  "Profilprodukter för kampanjer, mässor och onboarding",
  "Tryck, brodyr och leveransplanering för återkommande behov"
];

const categories = [
  "Arbetskläder",
  "Profilprodukter",
  "Giveaways",
  "Mässmaterial"
];

export default async function HomePage() {
  const catalog = await fetchPublicProducts();
  const products = catalog.products;

  return (
    <main className="bg-[#07162b] text-white">
      <section className="relative overflow-hidden border-b border-white/10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(242,139,57,0.28),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(18,51,95,0.55),transparent_45%)]" />
        <div className="relative mx-auto grid max-w-7xl gap-12 px-6 py-20 lg:grid-cols-[1.15fr_0.85fr] lg:px-8">
          <div className="space-y-8">
            <div className="inline-flex rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-[#f6a15d]">
              UNIFORMA
            </div>
            <div className="space-y-5">
              <h1 className="max-w-3xl text-5xl font-semibold leading-tight sm:text-6xl">
                Profilering &amp; Tryck för ditt företag
              </h1>
              <p className="max-w-2xl text-lg text-slate-200">
                Vi hjälper företag med arbetskläder, profilprodukter och tryck.
              </p>
            </div>
            <div className="flex flex-wrap gap-4">
              <a className="rounded-full bg-[#f28b39] px-6 py-3 text-sm font-semibold text-white" href="#quote-form">
                Begär offert
              </a>
              <Link className="rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white" href="/products">
                Se produkter
              </Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              {services.map((service) => (
                <div key={service} className="rounded-[1.75rem] border border-white/10 bg-white/5 p-5 text-sm text-slate-200">
                  {service}
                </div>
              ))}
            </div>
          </div>
          <div id="quote-form">
            <QuoteForm title="Begär offert" />
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-18 lg:px-8">
        <div className="grid gap-6 md:grid-cols-3">
          {services.map((service, index) => (
            <article key={service} className="rounded-[2rem] bg-white p-8 text-[#10233f] shadow-[0_20px_60px_rgba(2,12,27,0.22)]">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#f28b39]">Tjanst 0{index + 1}</p>
              <h2 className="mt-4 text-2xl font-semibold">{service}</h2>
            </article>
          ))}
        </div>
      </section>

      <section className="border-y border-white/10 bg-[#0b1d35]">
        <div className="mx-auto max-w-7xl px-6 py-18 lg:px-8">
          <div className="flex flex-wrap items-end justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#f28b39]">Produktkategorier</p>
              <h2 className="mt-2 text-3xl font-semibold text-white">Det vi levererar varje vecka</h2>
            </div>
            <Link className="text-sm font-semibold text-[#f6a15d]" href="/products">
              Se hela katalogen
            </Link>
          </div>
          <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {categories.map((category) => (
              <div key={category} className="rounded-[1.75rem] border border-white/10 bg-white/5 p-6">
                <p className="text-lg font-semibold">{category}</p>
              </div>
            ))}
          </div>
          <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {products.slice(0, 6).map((product) => (
              <Link key={product.product_id} className="rounded-[2rem] border border-white/10 bg-white/5 p-5" href={`/products/${product.slug}`}>
                <div className="overflow-hidden rounded-[1.5rem] bg-white/10">
                  <Image
                    src={product.primary_image || "/images/placeholder.webp"}
                    alt={product.name}
                    width={500}
                    height={500}
                    className="h-56 w-full object-cover"
                    loading="lazy"
                    sizes="(max-width:768px) 100vw, 25vw"
                  />
                </div>
                <div className="mt-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-300">
                    {product.category ?? product.brand ?? "Uniforma"}
                  </p>
                  <h3 className="mt-2 text-xl font-semibold text-white">{product.name}</h3>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <footer className="mx-auto max-w-7xl px-6 py-10 text-sm text-slate-300 lg:px-8">
        <div className="flex flex-col gap-3 border-t border-white/10 pt-6 md:flex-row md:items-center md:justify-between">
          <p>UNIFORMA levererar profilering, arbetsklader och tryck for foretag.</p>
          <div className="flex gap-4">
            <Link href="/products">Produkter</Link>
            <a href="#quote-form">Begär offert</a>
          </div>
        </div>
      </footer>
    </main>
  );
}
