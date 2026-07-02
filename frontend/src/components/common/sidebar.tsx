/**
 * Sidebar navigation component.
 * Enterprise SaaS sidebar inspired by Linear/Vercel with aurora accent.
 */

import { NavLink, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Briefcase,
  Users,
  Trophy,
  BarChart3,
  Settings,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { APP, ROUTES, ANIMATION } from "@/lib/constants";

const navItems = [
  { label: "Dashboard", href: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { label: "Jobs", href: ROUTES.JOBS, icon: Briefcase },
  { label: "Candidates", href: ROUTES.CANDIDATES, icon: Users },
  { label: "Rankings", href: ROUTES.RANKINGS, icon: Trophy },
  { label: "Analytics", href: ROUTES.ANALYTICS, icon: BarChart3 },
];

const bottomItems = [
  { label: "Settings", href: ROUTES.SETTINGS, icon: Settings },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-[260px] flex-col border-r border-white/[0.06] bg-surface/80 backdrop-blur-xl">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/20">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-semibold tracking-tight text-text">
            {APP.NAME}
          </span>
          <span className="text-[10px] font-medium uppercase tracking-widest text-muted">
            {APP.TAGLINE}
          </span>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-4 h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent" />

      {/* Main Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-muted/60">
          Platform
        </p>
        {navItems.map((item) => {
          const isActive =
            item.href === "/"
              ? location.pathname === "/"
              : location.pathname.startsWith(item.href);

          return (
            <NavLink key={item.href} to={item.href} className="block">
              <motion.div
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "text-text"
                    : "text-muted hover:text-text",
                )}
                whileHover={{ x: 2 }}
                transition={{ duration: ANIMATION.DURATION.FAST }}
              >
                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-lg bg-white/[0.06] border border-white/[0.06]"
                    transition={{
                      type: "spring",
                      stiffness: 350,
                      damping: 30,
                    }}
                  />
                )}
                <item.icon
                  className={cn(
                    "relative z-10 h-[18px] w-[18px] shrink-0",
                    isActive ? "text-primary" : "text-muted group-hover:text-text",
                  )}
                />
                <span className="relative z-10">{item.label}</span>
              </motion.div>
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Navigation */}
      <div className="space-y-1 px-3 pb-4">
        <div className="mx-1 mb-3 h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent" />
        {bottomItems.map((item) => {
          const isActive = location.pathname.startsWith(item.href);
          return (
            <NavLink key={item.href} to={item.href} className="block">
              <div
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-white/[0.06] text-text"
                    : "text-muted hover:bg-white/[0.04] hover:text-text",
                )}
              >
                <item.icon className="h-[18px] w-[18px] shrink-0" />
                <span>{item.label}</span>
              </div>
            </NavLink>
          );
        })}
      </div>

      {/* Version badge */}
      <div className="border-t border-white/[0.06] px-6 py-3">
        <p className="text-[10px] text-muted/50">v{APP.VERSION}</p>
      </div>
    </aside>
  );
}
