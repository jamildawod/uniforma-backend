import { Panel } from "@/components/ui/panel";
import { fetchAdminBrands } from "@/lib/api/server";

export default async function AdminBrandsPage() {
  const brands = await fetchAdminBrands();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">PIM</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Brands</h2>
        <div className="mt-6 space-y-3">
          {brands.map((brand) => (
            <div key={brand.id} className="rounded-2xl border border-slate-200 p-4">
              <p className="font-semibold text-ink">{brand.name}</p>
              <p className="text-sm text-slate-500">{brand.slug}</p>
            </div>
          ))}
          {brands.length === 0 ? <p className="text-sm text-slate-500">No brands available.</p> : null}
        </div>
      </Panel>
    </div>
  );
}
