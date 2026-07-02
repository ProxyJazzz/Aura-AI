/**
 * Jobs page — displays all job descriptions.
 */

import { Briefcase, Plus } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { EmptyState } from "@/components/common/empty-state";

export function JobsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Jobs"
        description="Manage job descriptions and view AI-ranked candidates."
        actions={
          <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30">
            <Plus className="h-4 w-4" />
            Create Job
          </button>
        }
      />
      <EmptyState
        icon={Briefcase}
        title="No jobs yet"
        description="Create your first job description to start receiving AI-powered candidate rankings."
        action={
          <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary/90">
            <Plus className="h-4 w-4" />
            Create Job
          </button>
        }
      />
    </div>
  );
}
