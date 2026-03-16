"use client";

import Image from "next/image";
import Link from "next/link";
import { Search, X } from "lucide-react";
import { useEffect, useState } from "react";

import { getSearchSuggestions } from "@/lib/api/client";
import type { SearchSuggestionItem } from "@/lib/types/products";

export function SearchBar({
  value,
  onChange
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  const [results, setResults] = useState<SearchSuggestionItem[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handle = setTimeout(async () => {
      if (value.trim().length < 2) {
        setResults([]);
        setOpen(false);
        return;
      }
      const response = await getSearchSuggestions(value.trim());
      setResults(response.items);
      setOpen(true);
    }, 300);

    return () => clearTimeout(handle);
  }, [value]);

  return (
    <div className="relative w-full">
      <div className="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-3 shadow-[0_14px_34px_rgba(16,35,63,0.08)]">
        <Search className="h-5 w-5 text-slate-400" />
        <input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Sök produkter, kategorier eller färger"
          className="w-full bg-transparent text-sm text-[#10233f] outline-none placeholder:text-slate-400"
        />
        {value ? (
          <button
            type="button"
            onClick={() => {
              onChange("");
              setResults([]);
              setOpen(false);
            }}
            className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
            aria-label="Rensa sökfält"
          >
            <X className="h-4 w-4" />
          </button>
        ) : null}
      </div>
      {open && results.length > 0 ? (
        <div className="absolute left-0 right-0 top-[calc(100%+0.75rem)] z-30 overflow-hidden rounded-[1.5rem] border border-slate-200 bg-white shadow-[0_24px_60px_rgba(16,35,63,0.18)]">
          {results.map((item) => (
            <Link
              key={`${item.type}-${item.product_id ?? item.value}`}
              href={item.href}
              className="flex items-center gap-4 border-b border-slate-100 px-4 py-3 last:border-b-0 hover:bg-slate-50"
              onClick={() => setOpen(false)}
            >
              <div className="flex h-14 w-14 items-center justify-center overflow-hidden rounded-2xl bg-slate-100">
                {item.type === "product" ? (
                  <Image
                    src={item.primary_image || "/images/placeholder.webp"}
                    alt={item.value}
                    width={64}
                    height={64}
                    sizes="64px"
                    className="h-14 w-14 object-cover"
                  />
                ) : (
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{item.type}</span>
                )}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-[#10233f]">{item.value}</p>
                <p className="text-xs text-slate-500">{item.subtitle || "Uniforma"}</p>
              </div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{item.type}</p>
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  );
}
