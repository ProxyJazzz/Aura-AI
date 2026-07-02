/**
 * AURA AI — Entry Point
 * Mounts the React application to the DOM.
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

const root = document.getElementById("root");

if (!root) {
  throw new Error("Root element not found. Ensure index.html contains <div id='root'></div>");
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
