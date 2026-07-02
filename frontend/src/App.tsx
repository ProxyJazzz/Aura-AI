/**
 * AURA AI — Application Root
 * Sets up the router with provider wrapping.
 */

import { RouterProvider } from "react-router-dom";
import { QueryProvider } from "@/app/providers";
import { router } from "@/app/routes";

export default function App() {
  return (
    <QueryProvider>
      <RouterProvider router={router} />
    </QueryProvider>
  );
}
