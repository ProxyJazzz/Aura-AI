# Frontend Architecture Document — AURA AI

## 1. Frontend Tech Stack
*   **Core:** React 18+ (Vite as build tool), TypeScript.
*   **Styling:** Vanilla CSS coupled with a modern layout system (CSS variables, CSS grid/flexbox).
*   **State Management:** Zustand (for lightweight, global state across job uploads, active profiles, and search filters).
*   **Icons:** Lucide-React.

---

## 2. Design System & Aesthetics
AURA AI employs an **AI-Native, Premium Dark Theme** UI inspired by Vercel, Linear, and Stripe.
*   **Color Palette (Dark Mode):**
    *   *Background:* `#09090b` (Deep obsidian black)
    *   *Card/Container Background:* `#18181b` (Muted dark gray)
    *   *Accent Primary:* `#ffffff` (Pure white)
    *   *Accent AI/Highlight:* HSL Tailored Neon Blue or Purple gradients for AI processing indications.
*   **Typography:** Outfit or Inter fonts (via Google Fonts) replacing standard system sans-serifs.
*   **Transitions:** Subtle hover animations (opacity transitions, scale scaling) for micro-interactions.
*   **Layouts:** Glassmorphic side navigation with smooth backdrops and responsive flex grids.

---

## 3. Page Structure & Component Library
*   **Dashboard Page (`/`):** Displays uploaded active Job Description overview, candidate match counts, search query bars, and categoric candidate breakdowns.
*   **Ranking Details Page (`/ranking`):** Exhibits the tabular, scrollable list of candidates sorted by rank, showing semantic scores, overall scores, and hiring decisions.
*   **Export View (`/export`):** Renders export manifests, downloads generated CSVs and recruiter report JSONs, and lists history tables.

---

## 4. API Integration & Polling Pattern
The frontend communicates using standard `fetch` or Axios clients. For async backend operations (e.g. ranking cache builds):
1.  Frontend triggers `POST /ranking/build`.
2.  Backend responds with `202 Accepted`.
3.  Frontend initiates a polling loop checking `GET /ranking/status` every 2 seconds.
4.  Once the status response indicates `is_built: true`, the loop terminates and lists the updated dataset page.
