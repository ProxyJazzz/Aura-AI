/**
 * Candidates page — displays all candidates across jobs.
 */

import { Users, Plus } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { EmptyState } from "@/components/common/empty-state";

export function CandidatesPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Candidates"
        description="View and manage candidate profiles across all positions."
        actions={
          <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30">
            <Plus className="h-4 w-4" />
            Add Candidate
          </button>
        }
      />
      <EmptyState
        icon={Users}
        title="No candidates yet"
        description="Add candidates to your jobs to start seeing AI-powered match scores and rankings."
        action={
          <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary/90">
            <Plus className="h-4 w-4" />
            Add Candidate
          </button>
        }
      />
    </div>
  );
}
