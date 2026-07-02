/**
 * Top navigation bar.
 * Displays breadcrumb-style page title and user actions.
 */

import { useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Search, Bell, User } from "lucide-react";
import { ANIMATION } from "@/lib/constants";

const routeTitles: Record<string, string> = {
  "/": "Dashboard",
  "/jobs": "Jobs",
  "/candidates": "Candidates",
  "/rankings": "Rankings",
  "/analytics": "Analytics",
  "/settings": "Settings",
};

export function TopNav() {
  const location = useLocation();
  const pageTitle = routeTitles[location.pathname] ?? "AURA AI";

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-white/[0.06] bg-background/60 px-8 backdrop-blur-xl">
      {/* Page Title */}
      <motion.h1
        key={pageTitle}
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: ANIMATION.DURATION.DEFAULT }}
        className="text-lg font-semibold text-text"
      >
        {pageTitle}
      </motion.h1>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {/* Search */}
        <button
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted transition-colors hover:bg-white/[0.06] hover:text-text"
          aria-label="Search"
        >
          <Search className="h-[18px] w-[18px]" />
        </button>

        {/* Notifications */}
        <button
          className="relative flex h-9 w-9 items-center justify-center rounded-lg text-muted transition-colors hover:bg-white/[0.06] hover:text-text"
          aria-label="Notifications"
        >
          <Bell className="h-[18px] w-[18px]" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-accent" />
        </button>

        {/* Divider */}
        <div className="mx-2 h-6 w-px bg-white/[0.06]" />

        {/* User Avatar */}
        <button
          className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-primary/80 to-accent/80 text-white transition-shadow hover:shadow-lg hover:shadow-primary/20"
          aria-label="User menu"
        >
          <User className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
