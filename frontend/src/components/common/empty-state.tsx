/**
 * Reusable empty state component.
 * Displayed when a list or section has no data.
 */

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { ANIMATION } from "@/lib/constants";

interface EmptyStateProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: ANIMATION.DURATION.DEFAULT }}
      className="flex flex-col items-center justify-center gap-4 py-16"
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/[0.04] text-muted">
        <Icon className="h-7 w-7" />
      </div>
      <div className="flex flex-col items-center gap-1.5 text-center">
        <h3 className="text-base font-semibold text-text">{title}</h3>
        <p className="max-w-sm text-sm text-muted">{description}</p>
      </div>
      {action && <div className="mt-2">{action}</div>}
    </motion.div>
  );
}
