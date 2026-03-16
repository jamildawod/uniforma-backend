import { AnalyticsOverview } from "@/components/admin/analytics-overview";
import { ErrorState } from "@/components/ui/error-state";
import { Panel } from "@/components/ui/panel";
import { fetchAdminAnalytics } from "@/lib/api/server";

export default async function AdminAnalyticsPage() {
  try {
    const analytics = await fetchAdminAnalytics();
    if (!analytics) {
      throw new Error("Analytics unavailable.");
    }

    return (
      <div className="space-y-6">
        <Panel>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-steel">Analytics</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">Catalog performance and inventory metrics</h2>
        </Panel>
        <AnalyticsOverview analytics={analytics} />
      </div>
    );
  } catch (error) {
    return <ErrorState title="Failed to load analytics" message={error instanceof Error ? error.message : "Unknown error"} />;
  }
}
