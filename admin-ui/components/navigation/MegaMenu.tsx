"use client";

import Link from "next/link";
import { useState } from "react";

import type { CategoryTreeNode } from "@/lib/types/products";

const fallbackCategories = [
  "Dental",
  "Djursjukvård",
  "Vård & Omsorg",
  "Städ & Service",
  "Kök",
  "Skönhet & Hälsa"
].map((name, index) => ({
  id: index + 1,
  name,
  slug: name.toLowerCase(),
  children: ["Byxor", "Tunikor", "Jackor", "Rockar", "Accessoarer"].map((child, childIndex) => ({
    id: (index + 1) * 10 + childIndex,
    name: child,
    slug: `${name.toLowerCase()}-${child.toLowerCase()}`,
    children: []
  }))
}));

export function MegaMenu({ categories }: { categories: CategoryTreeNode[] }) {
  const menu = categories.length ? categories : fallbackCategories;
  const [activeId, setActiveId] = useState<number>(menu[0]?.id ?? 0);
  const active = menu.find((item) => item.id === activeId) ?? menu[0];

  return (
    <div className="hidden rounded-[1.75rem] border border-white/10 bg-[#0c1a2f] text-white shadow-[0_20px_50px_rgba(2,12,27,0.18)] lg:block">
      <div className="flex">
        <div className="w-72 border-r border-white/10 p-3">
          {menu.map((category) => (
            <button
              key={category.id}
              type="button"
              onMouseEnter={() => setActiveId(category.id)}
              onFocus={() => setActiveId(category.id)}
              className={`flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left text-sm transition ${
                active?.id === category.id ? "bg-white/10 text-white" : "text-slate-300 hover:bg-white/5"
              }`}
            >
              <span>{category.name}</span>
              <span className="text-xs uppercase tracking-[0.2em] text-[#f6a15d]">Utforska</span>
            </button>
          ))}
        </div>
        <div className="flex-1 p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#f6a15d]">{active?.name}</p>
          <div className="mt-4 grid grid-cols-2 gap-4">
            {active?.children.map((child) => (
              <Link
                key={child.id}
                href={`/products?category=${encodeURIComponent(active.name)}`}
                className="rounded-[1.25rem] border border-white/10 bg-white/5 px-4 py-4 text-sm font-medium text-slate-100 transition hover:bg-white/10"
              >
                {child.name}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
