"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { useCreateProductImage } from "@/hooks/use-product-mutations";
import { imageSchema, type ImageInput } from "@/lib/schemas/overrides";
import type { ProductImage } from "@/lib/types/products";

export function ImageManager({
  productId,
  images
}: {
  productId: string;
  images: ProductImage[];
}) {
  const [message, setMessage] = useState<string | null>(null);
  const mutation = useCreateProductImage(productId);
  const form = useForm<ImageInput>({
    resolver: zodResolver(imageSchema),
    defaultValues: {
      url: "",
      is_primary: false,
      position: 0
    }
  });

  return (
    <div className="space-y-6">
      <div className="grid gap-3 md:grid-cols-2">
        {images.map((image) => (
          <div key={image.id} className="rounded-2xl border border-slate-200 p-4">
            <p className="truncate text-sm font-medium text-ink">{image.url}</p>
            <p className="mt-1 text-xs text-slate-500">Position {image.position}</p>
          </div>
        ))}
      </div>
      <form
        className="grid gap-3 md:grid-cols-2"
        onSubmit={form.handleSubmit(async (values) => {
          setMessage(null);
          try {
            await mutation.mutateAsync(values);
            form.reset();
            setMessage("Image queued successfully.");
          } catch (error) {
            setMessage(error instanceof Error ? error.message : "Failed to add image.");
          }
        })}
      >
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Image URL or /uploads path" {...form.register("url")} />
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Variant ID (optional)" {...form.register("variant_id")} />
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Position" type="number" {...form.register("position")} />
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input type="checkbox" {...form.register("is_primary")} />
          Primary image
        </label>
        <button className="rounded-2xl bg-ink px-4 py-3 text-sm font-semibold text-white" disabled={mutation.isPending} type="submit">
          {mutation.isPending ? "Saving..." : "Add image"}
        </button>
      </form>
      {message ? <p className="text-sm text-slate-600">{message}</p> : null}
    </div>
  );
}
