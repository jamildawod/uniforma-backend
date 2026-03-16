"use client";

import { SlidersHorizontal, X } from "lucide-react";
import { useMemo, useState } from "react";

import type { CatalogFilterOption } from "@/lib/types/products";

type FiltersState = {
  category?: string;
  color?: string;
  size?: string;
  price?: string;
};

function FilterGroup({
  label,
  items,
  value,
  onChange
}: {
  label: string;
  items: CatalogFilterOption[];
  value?: string;
  onChange: (value?: string) => void;
}) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-[#10233f]">{label}</h3>
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => onChange(undefined)}
          className={`rounded-full px-3 py-2 text-xs ${!value ? "bg-[#10233f] text-white" : "bg-slate-100 text-slate-600"}`}
        >
          Alla
        </button>
        {items.map((item) => (
          <button
            key={item.value}
            type="button"
            onClick={() => onChange(item.value)}
            className={`rounded-full px-3 py-2 text-xs ${
              value === item.value ? "bg-[#10233f] text-white" : "bg-slate-100 text-slate-600"
            }`}
          >
            {item.value} ({item.count})
          </button>
        ))}
      </div>
    </div>
  );
}

export function FilterSidebar({
  categories,
  colors,
  sizes,
  value,
  onChange
}: {
  categories: CatalogFilterOption[];
  colors: CatalogFilterOption[];
  sizes: CatalogFilterOption[];
  value: FiltersState;
  onChange: (next: FiltersState) => void;
}) {
  const [open, setOpen] = useState(false);
  const priceOptions = useMemo(
    () => [
      { value: "0-300", count: 0 },
      { value: "300-600", count: 0 },
      { value: "600+", count: 0 }
    ],
    []
  );

  const content = (
    <div className="space-y-8">
      <div className="flex items-center justify-between lg:hidden">
        <p className="text-base font-semibold text-[#10233f]">Filter</p>
        <button type="button" onClick={() => setOpen(false)} className="rounded-full p-2 text-slate-500">
          <X className="h-5 w-5" />
        </button>
      </div>
      <FilterGroup label="Kategori" items={categories} value={value.category} onChange={(category) => onChange({ ...value, category })} />
      <FilterGroup label="Färg" items={colors} value={value.color} onChange={(color) => onChange({ ...value, color })} />
      <FilterGroup label="Storlek" items={sizes} value={value.size} onChange={(size) => onChange({ ...value, size })} />
      <FilterGroup label="Pris" items={priceOptions} value={value.price} onChange={(price) => onChange({ ...value, price })} />
    </div>
  );

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-[#10233f] shadow-[0_12px_30px_rgba(16,35,63,0.08)] lg:hidden"
      >
        <SlidersHorizontal className="h-4 w-4" />
        Filter
      </button>
      <aside className="hidden w-72 shrink-0 rounded-[1.75rem] border border-slate-200 bg-white p-6 shadow-[0_18px_50px_rgba(16,35,63,0.08)] lg:block">
        {content}
      </aside>
      {open ? (
        <div className="fixed inset-0 z-40 bg-[#07162b]/45 lg:hidden">
          <div className="absolute bottom-0 left-0 right-0 max-h-[88vh] overflow-y-auto rounded-t-[2rem] bg-white p-6">
            {content}
          </div>
        </div>
      ) : null}
    </>
  );
}
