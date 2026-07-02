/**
 * Rankings page — displays AI-generated candidate rankings.
 */

import { Trophy } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { EmptyState } from "@/components/common/empty-state";

export function RankingsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Rankings"
        description="AI-generated candidate rankings with explainable scores."
      />
      <EmptyState
        icon={Trophy}
        title="No rankings available"
        description="Rankings are generated automatically when candidates are matched against job descriptions using our semantic AI engine."
      />
    </div>
  );
}
