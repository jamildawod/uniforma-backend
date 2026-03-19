"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";

type Category = {
  id: number;
  name: string;
  slug?: string | null;
};

// Static fallback — the 6 main sector categories
const STATIC_CATEGORIES: Category[] = [
  { id: 4,  name: "Dental",          slug: "dental" },
  { id: 10, name: "Djursjukvård",    slug: "djursjukvard" },
  { id: 34, name: "Skönhet & Hälsa", slug: "skonhet-halsa" },
  { id: 16, name: "Vård & Omsorg",   slug: "vard-omsorg" },
  { id: 22, name: "Städ & Service",  slug: "stad-service" },
  { id: 28, name: "Kök",             slug: "kok" },
];

export default function MegaMenu({
  categories = [],
}: {
  categories?: Category[];
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  const items = categories.length > 0 ? categories : STATIC_CATEGORIES;

  return (
    <div className="relative flex-shrink-0" ref={ref}>
      {/* TRIGGER BUTTON */}
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="flex items-center gap-2 rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
      >
        <span className="text-base leading-none">☰</span>
        Alla produkter
      </button>

      {/* DROPDOWN */}
      {open && (
        <div className="absolute left-0 top-full z-50 mt-2 w-[640px] rounded-xl border border-stone-200 bg-white p-6 shadow-2xl">
          <p className="mb-4 text-xs font-semibold uppercase tracking-widest text-stone-400">
            Produktkategorier
          </p>
          <div className="grid grid-cols-3 gap-3">
            {items.map((cat) => (
              <Link
                key={cat.id}
                href={`/shop?category=${encodeURIComponent(cat.slug ?? cat.name)}`}
                onClick={() => setOpen(false)}
                className="rounded-lg border border-stone-100 px-4 py-3 text-sm font-medium text-stone-800 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
              >
                {cat.name}
              </Link>
            ))}
          </div>
          <div className="mt-4 border-t border-stone-100 pt-4">
            <Link
              href="/shop"
              onClick={() => setOpen(false)}
              className="text-sm font-semibold text-blue-600 hover:underline"
            >
              Visa alla produkter →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
