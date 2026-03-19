"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";

type Category = {
  id: number;
  name: string;
  slug?: string | null;
};

const STATIC_CATEGORIES: Category[] = [
  { id: 4,  name: "Dental",          slug: "dental" },
  { id: 10, name: "Djursjukvård",    slug: "djursjukvard" },
  { id: 34, name: "Skönhet & Hälsa", slug: "skonhet-halsa" },
  { id: 16, name: "Vård & Omsorg",   slug: "vard-omsorg" },
  { id: 22, name: "Städ & Service",  slug: "stad-service" },
  { id: 28, name: "Kök",             slug: "kok" },
];

const NAV_LINKS = [
  { href: "/",              label: "Startsida" },
  { href: "/om-oss",        label: "Om oss" },
  { href: "/superdeal",     label: "Superdeal" },
  { href: "/storleksguide", label: "Storleksguide" },
];

export default function MegaMenu({
  categories,
}: {
  categories?: Category[] | null;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  const safeCategories = Array.isArray(categories) ? categories : [];
  const items = safeCategories.length > 0 ? safeCategories : STATIC_CATEGORIES;
  const allLinks = Array.isArray(NAV_LINKS) ? NAV_LINKS : [];

  return (
    <div className="w-full border-t border-b border-gray-200 bg-[#f7f7f7]">
      <div className="mx-auto max-w-6xl flex items-center overflow-x-auto">

        {/* ALLA PRODUKTER BUTTON */}
        <div className="relative flex-shrink-0 border-r border-gray-200" ref={ref}>
          <button
            onClick={() => setOpen(!open)}
            aria-expanded={open}
            className="flex items-center gap-2 h-[50px] px-5 bg-blue-600 text-white text-sm font-semibold transition hover:bg-blue-700 whitespace-nowrap"
          >
            <span className="text-base leading-none">☰</span>
            Alla produkter
          </button>

          {/* DROPDOWN */}
          {open && (
            <div className="absolute left-0 top-full z-50 mt-0 w-[600px] border border-gray-200 bg-white shadow-xl">
              <div className="p-5">
                <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-stone-400">
                  Produktkategorier
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {(items ?? []).map((cat) => (
                    <Link
                      key={cat?.id}
                      href={`/shop?category=${encodeURIComponent(cat?.slug ?? cat?.name ?? "")}`}
                      onClick={() => setOpen(false)}
                      className="rounded border border-stone-100 px-4 py-2.5 text-sm font-medium text-stone-800 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                    >
                      {cat?.name}
                    </Link>
                  ))}
                </div>
                <div className="mt-4 border-t border-stone-100 pt-3">
                  <Link
                    href="/shop"
                    onClick={() => setOpen(false)}
                    className="text-sm font-semibold text-blue-600 hover:underline"
                  >
                    Visa alla produkter →
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* NAV LINKS AS STRIP ITEMS */}
        {allLinks.map((link, index) => (
          <a
            key={link?.href ?? index}
            href={link?.href ?? "/"}
            className={`flex items-center h-[50px] px-6 text-sm font-medium text-gray-700 whitespace-nowrap transition hover:text-black hover:bg-gray-100${index < allLinks.length - 1 ? " border-r border-gray-200" : ""}`}
          >
            {link?.label}
          </a>
        ))}

      </div>
    </div>
  );
}
