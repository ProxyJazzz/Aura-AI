/**
 * Root application layout.
 * Wraps all pages with sidebar, top navigation, and content area.
 */

import { Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import { Sidebar } from "@/components/common/sidebar";
import { TopNav } from "@/components/common/top-nav";
import { ErrorBoundary } from "@/components/common/error-boundary";
import { ANIMATION } from "@/lib/constants";

export function RootLayout() {
  return (
    <div className="flex min-h-screen bg-background">
      {/* Ambient background effects */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute -left-[200px] -top-[200px] h-[600px] w-[600px] rounded-full bg-primary/[0.03] blur-[120px]" />
        <div className="absolute -bottom-[200px] -right-[200px] h-[600px] w-[600px] rounded-full bg-accent/[0.02] blur-[120px]" />
      </div>

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="relative z-10 ml-[260px] flex flex-1 flex-col">
        <TopNav />
        <main className="flex-1 p-8">
          <ErrorBoundary>
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: ANIMATION.DURATION.DEFAULT }}
            >
              <Outlet />
            </motion.div>
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
