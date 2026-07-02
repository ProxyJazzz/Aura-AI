/**
 * 404 Not Found page.
 * Premium error page with navigation back to dashboard.
 */

import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Compass } from "lucide-react";
import { ANIMATION, ROUTES } from "@/lib/constants";

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-8">
      {/* Ambient glow */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-1/3 h-[400px] w-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/[0.04] blur-[100px]" />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: ANIMATION.DURATION.SLOW }}
        className="relative flex flex-col items-center gap-6"
      >
        {/* Icon */}
        <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-white/[0.04] text-muted">
          <Compass className="h-10 w-10" />
        </div>

        {/* 404 */}
        <h1 className="bg-gradient-to-r from-primary to-accent bg-clip-text text-7xl font-extrabold tracking-tight text-transparent">
          404
        </h1>

        {/* Message */}
        <div className="flex flex-col items-center gap-2 text-center">
          <h2 className="text-xl font-semibold text-text">Page not found</h2>
          <p className="max-w-md text-sm text-muted">
            The page you're looking for doesn't exist or has been moved.
            Let's get you back on track.
          </p>
        </div>

        {/* Action */}
        <button
          onClick={() => navigate(ROUTES.DASHBOARD)}
          className="flex items-center gap-2 rounded-lg bg-white/[0.06] px-5 py-2.5 text-sm font-medium text-text transition-colors hover:bg-white/[0.1]"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>
      </motion.div>
    </div>
  );
}
