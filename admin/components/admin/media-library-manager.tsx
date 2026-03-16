"use client";

import { useState, useTransition } from "react";

import { deleteAdminMedia, uploadAdminImage } from "@/lib/api/client";
import type { MediaItem } from "@/lib/types/products";

export function MediaLibraryManager({ initialMedia }: { initialMedia: MediaItem[] }) {
  const [media, setMedia] = useState(initialMedia);
  const [message, setMessage] = useState("");
  const [pending, startTransition] = useTransition();

  function onUpload(file: File) {
    startTransition(async () => {
      setMessage("");
      try {
        const uploaded = await uploadAdminImage(file);
        setMedia((current) => [{ filename: uploaded.filename, url: uploaded.url }, ...current]);
        setMessage("Image uploaded.");
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Upload failed.");
      }
    });
  }

  function remove(filename: string) {
    startTransition(async () => {
      setMessage("");
      try {
        await deleteAdminMedia(filename);
        setMedia((current) => current.filter((item) => item.filename !== filename));
        setMessage("Image deleted.");
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Delete failed.");
      }
    });
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-white p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-ink">Upload image</p>
            <p className="text-sm text-slate-500">Images are stored in the existing backend uploads pipeline.</p>
          </div>
          <label className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white">
            Select file
            <input className="hidden" type="file" accept="image/*" onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onUpload(file);
              event.currentTarget.value = "";
            }} />
          </label>
        </div>
      </div>

      {message ? <p className="text-sm text-slate-600">{message}</p> : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {media.map((item) => (
          <div key={item.filename} className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
            <img alt={item.filename} className="h-48 w-full object-cover" src={item.url} />
            <div className="flex items-center justify-between gap-3 p-4">
              <p className="truncate text-sm font-medium text-ink">{item.filename}</p>
              <button className="text-sm font-medium text-red-600" disabled={pending} onClick={() => remove(item.filename)} type="button">Delete</button>
            </div>
          </div>
        ))}
        {media.length === 0 ? <p className="text-sm text-slate-500">No media uploaded yet.</p> : null}
      </div>
    </div>
  );
}
