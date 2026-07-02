/**
 * Analytics page — displays hiring analytics and insights.
 */

import { BarChart3 } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { EmptyState } from "@/components/common/empty-state";

export function AnalyticsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Analytics"
        description="Hiring funnel analytics, score distributions, and pipeline insights."
      />
      <EmptyState
        icon={BarChart3}
        title="No analytics data"
        description="Analytics will populate as you create jobs, add candidates, and generate rankings."
      />
    </div>
  );
}
