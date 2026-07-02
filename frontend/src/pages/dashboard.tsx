/**
 * Dashboard page — the main landing view.
 * Shows platform overview with key metrics and recent activity.
 */

import { motion } from "framer-motion";
import {
  Briefcase,
  Users,
  Trophy,
  TrendingUp,
  ArrowUpRight,
  Sparkles,
} from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { ANIMATION } from "@/lib/constants";

const stats = [
  {
    label: "Active Jobs",
    value: "—",
    change: null,
    icon: Briefcase,
    gradient: "from-primary/20 to-primary/5",
    iconColor: "text-primary",
  },
  {
    label: "Total Candidates",
    value: "—",
    change: null,
    icon: Users,
    gradient: "from-accent/20 to-accent/5",
    iconColor: "text-accent",
  },
  {
    label: "Rankings Generated",
    value: "—",
    change: null,
    icon: Trophy,
    gradient: "from-success/20 to-success/5",
    iconColor: "text-success",
  },
  {
    label: "Avg. Match Score",
    value: "—",
    change: null,
    icon: TrendingUp,
    gradient: "from-warning/20 to-warning/5",
    iconColor: "text-warning",
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0 },
};

export function DashboardPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Dashboard"
        description="Welcome to AURA AI — your AI recruitment intelligence platform."
      />

      {/* Stats Grid */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4"
      >
        {stats.map((stat) => (
          <motion.div
            key={stat.label}
            variants={item}
            transition={{ duration: ANIMATION.DURATION.DEFAULT }}
            className="group relative overflow-hidden rounded-xl border border-white/[0.06] bg-surface/50 p-6 backdrop-blur-sm transition-all hover:border-white/[0.1] hover:bg-surface/70"
          >
            {/* Gradient background */}
            <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-0 transition-opacity group-hover:opacity-100`} />

            <div className="relative z-10 flex items-start justify-between">
              <div className="flex flex-col gap-3">
                <p className="text-xs font-medium uppercase tracking-wider text-muted">
                  {stat.label}
                </p>
                <p className="text-3xl font-bold tracking-tight text-text">
                  {stat.value}
                </p>
                {stat.change && (
                  <div className="flex items-center gap-1 text-xs text-success">
                    <ArrowUpRight className="h-3 w-3" />
                    <span>{stat.change}</span>
                  </div>
                )}
              </div>
              <div className={`flex h-10 w-10 items-center justify-center rounded-xl bg-white/[0.04] ${stat.iconColor}`}>
                <stat.icon className="h-5 w-5" />
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Quick Start / Getting Started */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: ANIMATION.DURATION.DEFAULT, delay: 0.3 }}
        className="overflow-hidden rounded-xl border border-white/[0.06] bg-surface/50 p-8 backdrop-blur-sm"
      >
        <div className="flex items-start gap-6">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-accent/20 text-primary">
            <Sparkles className="h-6 w-6" />
          </div>
          <div className="flex flex-col gap-2">
            <h3 className="text-lg font-semibold text-text">
              Ready to hire beyond keywords
            </h3>
            <p className="max-w-2xl text-sm leading-relaxed text-muted">
              AURA AI uses semantic AI to deeply understand job descriptions and
              candidate profiles. Create your first job description to start
              receiving AI-powered candidate rankings with explainable
              recommendations.
            </p>
            <div className="mt-3 flex items-center gap-3">
              <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary/25 transition-all hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30">
                <Briefcase className="h-4 w-4" />
                Create First Job
              </button>
              <button className="flex items-center gap-2 rounded-lg border border-white/[0.1] bg-white/[0.04] px-4 py-2.5 text-sm font-medium text-text transition-colors hover:bg-white/[0.08]">
                Learn More
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
