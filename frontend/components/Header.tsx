"use client";

import Link from "next/link";
import MegaMenu from "@/components/navigation/MegaMenu";

const NAV_LINKS = [
  { href: "/",               label: "Startsida" },
  { href: "/om-oss",         label: "Om oss" },
  { href: "/superdeal",      label: "Superdeal" },
  { href: "/storleksguide",  label: "Storleksguide" },
];

export function Header() {
  return (
    <header className="border-b border-stone-100 bg-white">
      {/* TOP BAR — Logo + Search + Contact */}
      <div className="mx-auto flex h-[70px] max-w-6xl items-center justify-between gap-6 px-8">
        <Link href="/" className="flex-shrink-0">
          <img
            src="/UNIFORMA_LIGGANDE_SVART.png"
            alt="Uniforma"
            className="h-12 md:h-16 lg:h-20 w-auto object-contain"
          />
        </Link>

        <form className="flex w-full max-w-xl flex-1 items-center rounded-[32px] border border-stone-200 bg-stone-50 px-5 py-2 shadow-sm transition focus-within:border-stone-300">
          <label htmlFor="uniforma-search" className="sr-only">
            Sök produkter
          </label>
          <input
            id="uniforma-search"
            name="q"
            type="search"
            placeholder="Sök produkter, kategorier eller varumärken..."
            className="w-full border-none bg-transparent text-sm font-medium text-stone-800 placeholder:text-stone-400 focus:outline-none"
          />
        </form>

        <a
          href="/kontakt"
          className="ml-4 rounded-full border border-stone-900 bg-stone-900 px-6 py-2 text-sm font-semibold uppercase tracking-wide text-white transition hover:bg-stone-800"
        >
          Kontakt
        </a>
      </div>

      {/* NAV BAR — MegaMenu + Nav links */}
      <div className="border-t border-stone-100 bg-white">
        <div className="mx-auto flex max-w-6xl items-center gap-6 px-8 py-2">
          <MegaMenu />
          <nav className="flex items-center gap-6">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-stone-600 transition hover:text-stone-900"
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
