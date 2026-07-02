import React from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

export type AuraState = "idle" | "processing" | "thinking" | "completed" | "alert"

interface AuraPulseProps {
  state?: AuraState
  className?: string
  size?: number
}

export function AuraPulse({ state = "idle", className, size = 24 }: AuraPulseProps) {
  // Define animation states for the core orb
  const orbVariants = {
    idle: {
      scale: [1, 1.05, 1],
      opacity: [0.6, 0.8, 0.6],
      backgroundColor: "#3B82F6", // Primary
      boxShadow: "0 0 10px rgba(59, 130, 246, 0.4)",
      transition: { duration: 3, repeat: Infinity, ease: "easeInOut" }
    },
    processing: {
      scale: [1, 1.2, 1],
      opacity: [0.7, 1, 0.7],
      backgroundColor: "#38BDF8", // Secondary
      boxShadow: "0 0 15px rgba(56, 189, 248, 0.6)",
      transition: { duration: 1.5, repeat: Infinity, ease: "easeInOut" }
    },
    thinking: {
      scale: [0.9, 1.1, 0.9],
      opacity: [0.4, 0.9, 0.4],
      backgroundColor: "#22D3EE", // Accent
      boxShadow: "0 0 20px rgba(34, 211, 238, 0.8)",
      transition: { duration: 0.8, repeat: Infinity, ease: "easeInOut" }
    },
    completed: {
      scale: [1, 1.1, 1],
      opacity: 1,
      backgroundColor: "#22C55E", // Success
      boxShadow: "0 0 10px rgba(34, 197, 94, 0.4)",
      transition: { duration: 0.5, repeat: 0, ease: "easeOut" }
    },
    alert: {
      scale: [1, 1.15, 1],
      opacity: [0.8, 1, 0.8],
      backgroundColor: "#EF4444", // Danger
      boxShadow: "0 0 15px rgba(239, 68, 68, 0.6)",
      transition: { duration: 0.5, repeat: Infinity, ease: "easeInOut" }
    }
  }

  // Outer ring for breathing effect
  const ringVariants = {
    idle: {
      scale: [1, 1.5, 1],
      opacity: [0.1, 0.3, 0.1],
      border: "1px solid rgba(59, 130, 246, 0.2)",
      transition: { duration: 3, repeat: Infinity, ease: "easeInOut" }
    },
    processing: {
      scale: [1, 1.8, 1],
      opacity: [0.2, 0.5, 0.2],
      border: "1px solid rgba(56, 189, 248, 0.3)",
      transition: { duration: 1.5, repeat: Infinity, ease: "easeInOut" }
    },
    thinking: {
      scale: [0.8, 2, 0.8],
      opacity: [0.1, 0.6, 0.1],
      border: "1px solid rgba(34, 211, 238, 0.4)",
      transition: { duration: 0.8, repeat: Infinity, ease: "easeInOut" }
    },
    completed: {
      scale: 1.2,
      opacity: 0,
      border: "1px solid rgba(34, 197, 94, 0.5)",
      transition: { duration: 0.5 }
    },
    alert: {
      scale: [1, 1.6, 1],
      opacity: [0.3, 0.6, 0.3],
      border: "1px solid rgba(239, 68, 68, 0.5)",
      transition: { duration: 0.5, repeat: Infinity, ease: "easeInOut" }
    }
  }

  return (
    <div 
      className={cn("relative flex items-center justify-center", className)}
      style={{ width: size, height: size }}
    >
      <motion.div
        className="absolute inset-0 rounded-full"
        variants={ringVariants}
        animate={state}
        initial="idle"
      />
      <motion.div
        className="rounded-full"
        style={{ width: size * 0.5, height: size * 0.5 }}
        variants={orbVariants}
        animate={state}
        initial="idle"
      />
    </div>
  )
}
