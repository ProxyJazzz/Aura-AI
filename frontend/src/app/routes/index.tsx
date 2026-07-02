/**
 * Application route definitions.
 * Single source of truth for all client-side routes.
 */

import { createBrowserRouter } from "react-router-dom";
import { RootLayout } from "@/app/layouts/root-layout";
import { DashboardPage } from "@/pages/dashboard";
import { JobsPage } from "@/pages/jobs";
import { CandidatesPage } from "@/pages/candidates";
import { RankingsPage } from "@/pages/rankings";
import { AnalyticsPage } from "@/pages/analytics";
import { SettingsPage } from "@/pages/settings";
import { NotFoundPage } from "@/pages/not-found";
import { UploadPage } from "@/pages/upload";
import { ReportsPage } from "@/pages/reports";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "jobs", element: <JobsPage /> },
      { path: "candidates", element: <CandidatesPage /> },
      { path: "upload", element: <UploadPage /> },
      { path: "rankings", element: <RankingsPage /> },
      { path: "analytics", element: <AnalyticsPage /> },
      { path: "reports", element: <ReportsPage /> },
      { path: "settings", element: <SettingsPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
