/**
 * Application-wide constants.
 * All magic strings and configuration values live here.
 */

export const APP = {
  NAME: "AURA AI",
  TAGLINE: "Hiring Beyond Keywords.",
  VERSION: "1.0.0",
  DESCRIPTION:
    "AI Recruitment Intelligence Platform that semantically understands candidates and produces explainable rankings.",
} as const;

export const API = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  V1_PREFIX: "/api/v1",
  TIMEOUT_MS: 15_000,
} as const;

export const ROUTES = {
  DASHBOARD: "/",
  JOBS: "/jobs",
  CANDIDATES: "/candidates",
  RANKINGS: "/rankings",
  ANALYTICS: "/analytics",
  SETTINGS: "/settings",
} as const;

export const QUERY_KEYS = {
  HEALTH: ["health"] as const,
  JOBS: ["jobs"] as const,
  CANDIDATES: ["candidates"] as const,
  RANKINGS: ["rankings"] as const,
  ANALYTICS: ["analytics"] as const,
} as const;

export const ANIMATION = {
  DURATION: {
    FAST: 0.15,
    DEFAULT: 0.25,
    SLOW: 0.4,
    ENTER: 0.3,
    EXIT: 0.2,
  },
  EASE: {
    DEFAULT: [0.25, 0.1, 0.25, 1.0] as const,
    IN: [0.4, 0.0, 1.0, 1.0] as const,
    OUT: [0.0, 0.0, 0.2, 1.0] as const,
    IN_OUT: [0.4, 0.0, 0.2, 1.0] as const,
    SPRING: { type: "spring", stiffness: 300, damping: 30 } as const,
  },
} as const;

export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  "2XL": 1536,
} as const;
