"use client";

import Image from "next/image";
import { useState } from "react";

type GalleryImage = {
  id: number | string;
  url: string;
  alt: string;
};

export function ProductGallery({ images, fallbackAlt }: { images: GalleryImage[]; fallbackAlt: string }) {
  const [active, setActive] = useState(0);
  const current = images[active] ?? images[0];

  return (
    <div className="space-y-4">
      <div className="overflow-hidden rounded-[2rem] bg-white shadow-[0_18px_50px_rgba(16,35,63,0.08)]">
        <Image
          src={current?.url || "/images/placeholder.webp"}
          alt={current?.alt || fallbackAlt}
          width={1200}
          height={1200}
          sizes="(max-width:768px) 50vw, (max-width:1200px) 33vw, 25vw"
          priority
          className="h-[28rem] w-full object-cover"
        />
      </div>
      <div className="grid grid-cols-4 gap-3">
        {images.map((image, index) => (
          <button
            key={image.id}
            type="button"
            onClick={() => setActive(index)}
            className={`overflow-hidden rounded-2xl border ${index === active ? "border-[#10233f]" : "border-slate-200"} bg-white`}
          >
            <Image
              src={image.url}
              alt={image.alt}
              width={240}
              height={240}
              sizes="120px"
              loading="lazy"
              className="h-20 w-full object-cover"
            />
          </button>
        ))}
      </div>
    </div>
  );
}
