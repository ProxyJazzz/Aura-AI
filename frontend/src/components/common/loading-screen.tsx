/**
 * Loading screen displayed during initial app load.
 * Features the AURA AI logo with a pulsing animation.
 */

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { APP } from "@/lib/constants";

export function LoadingScreen() {
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center bg-background">
      {/* Ambient glow */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/5 blur-[120px]" />
      </div>

      <motion.div
        className="relative flex flex-col items-center gap-6"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        {/* Logo */}
        <motion.div
          className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent shadow-2xl shadow-primary/30"
          animate={{ boxShadow: [
            "0 0 30px rgba(124, 92, 255, 0.3)",
            "0 0 60px rgba(124, 92, 255, 0.15)",
            "0 0 30px rgba(124, 92, 255, 0.3)",
          ]}}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        >
          <Sparkles className="h-8 w-8 text-white" />
        </motion.div>

        {/* App name */}
        <div className="flex flex-col items-center gap-1">
          <h1 className="text-2xl font-bold tracking-tight text-text">
            {APP.NAME}
          </h1>
          <p className="text-sm text-muted">{APP.TAGLINE}</p>
        </div>

        {/* Loading bar */}
        <div className="h-0.5 w-48 overflow-hidden rounded-full bg-white/[0.06]">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
            initial={{ x: "-100%" }}
            animate={{ x: "100%" }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>
      </motion.div>
    </div>
  );
}
