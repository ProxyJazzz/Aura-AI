/**
 * Page header component with title, description, and optional actions.
 * Provides consistent page-level heading across all pages.
 */

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { ANIMATION } from "@/lib/constants";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: ANIMATION.DURATION.DEFAULT }}
      className="flex items-start justify-between gap-4"
    >
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold tracking-tight text-text">{title}</h2>
        {description && (
          <p className="text-sm text-muted">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </motion.div>
  );
}
