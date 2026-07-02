/**
 * Settings page — user profile and application configuration.
 */

import { motion } from "framer-motion";
import { User, Shield, Sliders, Bell } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { ANIMATION } from "@/lib/constants";

const sections = [
  {
    title: "Profile",
    description: "Manage your account details and preferences.",
    icon: User,
  },
  {
    title: "Security",
    description: "Password, sessions, and authentication settings.",
    icon: Shield,
  },
  {
    title: "Scoring Defaults",
    description: "Configure default AI scoring weights for new jobs.",
    icon: Sliders,
  },
  {
    title: "Notifications",
    description: "Email and in-app notification preferences.",
    icon: Bell,
  },
];

export function SettingsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Settings"
        description="Manage your account and platform configuration."
      />

      <div className="grid gap-4">
        {sections.map((section, i) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: ANIMATION.DURATION.DEFAULT,
              delay: i * 0.06,
            }}
            className="group flex cursor-pointer items-center gap-5 rounded-xl border border-white/[0.06] bg-surface/50 p-6 transition-all hover:border-white/[0.1] hover:bg-surface/70"
          >
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/[0.04] text-muted transition-colors group-hover:bg-primary/10 group-hover:text-primary">
              <section.icon className="h-5 w-5" />
            </div>
            <div className="flex flex-col gap-0.5">
              <h3 className="text-sm font-semibold text-text">{section.title}</h3>
              <p className="text-sm text-muted">{section.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
