"use client";

import { useState, useTransition } from "react";

import { createAdminCategory, deleteAdminCategory, updateAdminCategory } from "@/lib/api/client";
import type { Category } from "@/lib/types/products";

export function CategoryManager({ initialCategories }: { initialCategories: Category[] }) {
  const [categories, setCategories] = useState(initialCategories);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({ name: "", slug: "", parent_id: "", position: 0 });
  const [message, setMessage] = useState("");
  const [pending, startTransition] = useTransition();

  function reset() {
    setEditingId(null);
    setForm({ name: "", slug: "", parent_id: "", position: 0 });
  }

  function beginEdit(category: Category) {
    setEditingId(category.id);
    setForm({
      name: category.name,
      slug: category.slug,
      parent_id: category.parent_id ? String(category.parent_id) : "",
      position: category.position,
    });
  }

  function submit() {
    startTransition(async () => {
      setMessage("");
      try {
        const payload = {
          name: form.name,
          slug: form.slug || null,
          parent_id: form.parent_id ? Number(form.parent_id) : null,
          position: Number(form.position) || 0,
        };
        const result = editingId
          ? await updateAdminCategory(editingId, payload)
          : await createAdminCategory(payload);
        setCategories((current) => {
          const next = editingId ? current.map((item) => (item.id === result.id ? result : item)) : [...current, result];
          return next.sort((a, b) => a.position - b.position || a.name.localeCompare(b.name));
        });
        setMessage(editingId ? "Category updated." : "Category created.");
        reset();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Failed to save category.");
      }
    });
  }

  function remove(categoryId: number) {
    startTransition(async () => {
      setMessage("");
      try {
        await deleteAdminCategory(categoryId);
        setCategories((current) => current.filter((item) => item.id !== categoryId));
        if (editingId === categoryId) {
          reset();
        }
        setMessage("Category deleted.");
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Failed to delete category.");
      }
    });
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-6 md:grid-cols-2 xl:grid-cols-4">
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Category name" value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} />
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" placeholder="Slug" value={form.slug} onChange={(event) => setForm((current) => ({ ...current, slug: event.target.value }))} />
        <select className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" value={form.parent_id} onChange={(event) => setForm((current) => ({ ...current, parent_id: event.target.value }))}>
          <option value="">No parent</option>
          {categories.filter((item) => item.id !== editingId).map((category) => (
            <option key={category.id} value={category.id}>{category.name}</option>
          ))}
        </select>
        <input className="rounded-2xl border border-slate-200 px-4 py-3 text-sm" type="number" placeholder="Position" value={form.position} onChange={(event) => setForm((current) => ({ ...current, position: Number(event.target.value) }))} />
        <div className="flex gap-3 md:col-span-2 xl:col-span-4">
          <button className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white" disabled={pending || !form.name.trim()} onClick={submit} type="button">
            {editingId ? "Save category" : "Add category"}
          </button>
          {editingId ? <button className="rounded-full border border-slate-200 px-5 py-3 text-sm font-semibold" onClick={reset} type="button">Cancel</button> : null}
        </div>
      </div>

      {message ? <p className="text-sm text-slate-600">{message}</p> : null}

      <div className="overflow-hidden rounded-3xl bg-white shadow-panel">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Name</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Slug</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Parent</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Position</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {categories.map((category) => (
              <tr key={category.id}>
                <td className="px-4 py-4 font-medium text-ink">{category.name}</td>
                <td className="px-4 py-4 text-slate-600">{category.slug}</td>
                <td className="px-4 py-4 text-slate-600">{categories.find((item) => item.id === category.parent_id)?.name ?? "Top level"}</td>
                <td className="px-4 py-4 text-slate-600">{category.position}</td>
                <td className="px-4 py-4">
                  <div className="flex gap-3">
                    <button className="text-sm font-medium text-clay" onClick={() => beginEdit(category)} type="button">Edit</button>
                    <button className="text-sm font-medium text-red-600" onClick={() => remove(category.id)} type="button">Delete</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
