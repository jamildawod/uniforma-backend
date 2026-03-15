import { Panel } from "@/components/ui/panel";
import { fetchAdminQuotes } from "@/lib/api/server";

export default async function AdminQuotesPage() {
  const quotes = await fetchAdminQuotes();

  return (
    <div className="space-y-6">
      <Panel>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Quotes</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Quote requests</h2>
        <div className="mt-6 space-y-4">
          {quotes.map((quote) => (
            <article key={quote.id} className="rounded-2xl border border-slate-200 p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-ink">{quote.company || quote.name}</h3>
                  <p className="text-sm text-slate-500">{quote.email}</p>
                </div>
                <div className="text-right text-sm text-slate-500">
                  <p className="uppercase tracking-[0.16em]">{quote.status}</p>
                  <p>{new Date(quote.created_at).toLocaleString()}</p>
                </div>
              </div>
              <p className="mt-4 text-sm text-slate-700">{quote.message}</p>
            </article>
          ))}
          {quotes.length === 0 ? <p className="text-sm text-slate-500">No quote requests available.</p> : null}
        </div>
      </Panel>
    </div>
  );
}
