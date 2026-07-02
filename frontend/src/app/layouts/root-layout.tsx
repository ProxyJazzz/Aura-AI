/**
 * Root application layout.
 * Wraps all pages with sidebar, top navigation, and content area.
 */

import { Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import { Sidebar } from "@/components/common/sidebar";
import { TopNav } from "@/components/common/top-nav";
import { ErrorBoundary } from "@/components/common/error-boundary";
import { CommandPalette } from "@/components/common/command-palette";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ANIMATION } from "@/lib/constants";

export function RootLayout() {
  return (
    <TooltipProvider delayDuration={150}>
      <div className="flex min-h-screen bg-background text-text font-sans antialiased selection:bg-primary/30 selection:text-primary">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <div className="relative z-10 ml-[260px] flex flex-1 flex-col min-w-0">
          <TopNav />
          <main className="flex-1 p-8 xl:p-10 2xl:p-12 overflow-x-hidden">
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
        
        {/* Global Modals / Overlays */}
        <CommandPalette />
      </div>
    </TooltipProvider>
  );
}
