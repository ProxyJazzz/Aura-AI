# User Journey Maps

> AURA AI — Product Documentation
> Version: 1.0 | Last Updated: 2026-07-02 | Author: AURA Engineering

---

## 1. Purpose

This document maps the complete end-to-end user journeys through AURA AI for each primary persona. Each journey defines the sequence of actions, system responses, decision points, emotional states, and touchpoints that a user experiences while accomplishing their goals.

These journeys inform page design, navigation structure, API endpoint requirements, loading state behavior, and animation timing throughout the application.

---

## 2. Scope

This document covers:

- Primary user journeys for all core workflows
- Step-by-step flows with system responses
- Decision trees at key branching points
- Error paths and recovery flows
- Emotional journey mapping (frustration points, delight moments)
- Cross-persona journey intersections

This document does **not** cover UI component specifications (see [../06_FRONTEND/COMPONENT_LIBRARY.md](../06_FRONTEND/COMPONENT_LIBRARY.md)) or API implementation details (see [../05_BACKEND/API_SPECIFICATION.md](../05_BACKEND/API_SPECIFICATION.md)).

---

## 3. Business Context

User journeys directly translate to:

- **Time-to-value**: How quickly a recruiter goes from login to seeing ranked candidates
- **Adoption friction**: Where users get stuck and abandon the tool
- **Feature discovery**: How users encounter and adopt secondary features
- **Retention drivers**: Which workflows deliver enough value to create daily usage habits

The target is that a new user (Sarah Chen persona) completes their first successful ranking within **5 minutes of first login**.

---

## 4. Technical Context

Each step in a user journey maps to:

| Journey Element | Technical Artifact |
|---|---|
| User action | Frontend event handler → API call |
| System response | API endpoint → service layer → response |
| Loading state | Skeleton/spinner component with timing threshold |
| Error state | Error boundary → error component with recovery CTA |
| Navigation | React Router route transition with Framer Motion animation |
| Data display | React Query cache → component render |

---

## 5. Journey 1: First-Time Setup & Onboarding

**Persona**: Sarah Chen (Recruiter) / Alex Torres (Admin)
**Goal**: Register, create first job, add candidates, see ranked results
**Time Target**: < 5 minutes to first value

### 5.1 Flow Diagram

```
[Landing] → [Register] → [Dashboard (Empty)] → [Create JD] → [JD Detail]
                                                                    ↓
                                                              [Add Candidate] → [Add More?]
                                                                    ↓               ↓ Yes
                                                              [View Rankings] ← ← ← ┘
                                                                    ↓
                                                              [Explore Score] → [First Value ✓]
```

### 5.2 Step-by-Step Flow

| Step | User Action | System Response | UI State | Emotional State |
|---|---|---|---|---|
| 1 | Opens AURA AI URL | Displays login page with aurora gradient background, clear "Get Started" CTA | Login page with registration option | Curious, evaluating |
| 2 | Clicks "Create Account" | Shows registration form: name, email, password | Smooth slide transition to registration form | Neutral |
| 3 | Fills form, clicks "Register" | Validates input, creates user, issues JWT, redirects to dashboard | Form validation in real-time, success animation on submit | Hopeful |
| 4 | Sees empty dashboard | Displays professional empty state with illustration: "Create your first job to get started" | Empty state with single prominent CTA: "+ Create Job" | Slightly uncertain — "now what?" |
| 5 | Clicks "+ Create Job" | Opens JD creation panel (slide-in from right or modal) | Form with smart defaults, placeholder hints showing examples | Engaged, filling in details |
| 6 | Fills JD fields (title, description, skills, experience) | Real-time JD quality indicator updates as they type. Skill tags auto-suggest. | Quality score bar animates, skill chips appear with micro-animation | Guided, feels productive |
| 7 | Clicks "Create Job" | Saves JD, generates embedding (< 2 sec), redirects to JD detail page | Success toast with confetti-subtle animation, transition to JD detail | Satisfied — first milestone |
| 8 | Sees JD detail with empty candidate list | Displays candidate empty state: "Add your first candidate" with CTA | Empty state with "+ Add Candidate" button and optional "Import CSV" link | Ready to continue |
| 9 | Clicks "+ Add Candidate" | Opens candidate form (slide-in panel) | Form with structured fields: name, skills, experience, summary | Focused on data entry |
| 10 | Fills candidate fields, clicks "Save" | Saves candidate, triggers AI scoring pipeline (< 3 sec) | Brief scoring animation (pulsing score indicator), then score appears | Anticipation → Delight (first score!) |
| 11 | Adds 2-3 more candidates | Each triggers individual scoring. List re-sorts as scores arrive. | Candidates animate into their ranked position. Scores appear with count-up animation | Building confidence in the tool |
| 12 | Reviews ranked list | Displays candidates sorted by score with color-coded score badges | Score bars, confidence indicators, summary explanations visible | **Peak delight** — "This actually works" |
| 13 | Clicks on a candidate | Expands candidate detail with full score breakdown and explanation | Slide-in panel with animated score breakdown chart | Understanding, trust building |
| 14 | Reads AI explanation | Displays natural language explanation of why this candidate scored as they did | Highlighted strengths in green, gaps in amber, clear confidence level | **"Aha" moment** — this is why AURA matters |

### 5.3 Error Paths

| Error | Trigger | Recovery |
|---|---|---|
| Registration: email already exists | Duplicate email submission | "This email is already registered. Log in instead?" with link to login |
| Registration: weak password | Password doesn't meet complexity | Real-time password strength indicator with specific requirements shown |
| JD creation: too short description | Description < 50 characters | Inline validation: "Add more detail to help AURA AI understand this role better" |
| Candidate save: duplicate email | Same email for same job | "A candidate with this email already exists for this job" with link to view them |
| AI scoring fails | Model loading error or timeout | Score shows "Pending" with automatic retry. User sees: "Scoring in progress..." |

---

## 6. Journey 2: Daily Candidate Review

**Persona**: Sarah Chen (Recruiter)
**Goal**: Review new candidates, update pipeline, prepare shortlist
**Time Target**: < 15 minutes for 20-30 candidate review

### 6.1 Flow Diagram

```
[Login] → [Dashboard] → [Select Job] → [Review Ranked List]
                                              ↓
                                        [Quick Review Loop]
                                        ┌─────┴─────┐
                                        ↓            ↓
                                  [View Detail]  [Update Status]
                                        ↓            ↓
                                  [Add Note]   [Move to Shortlist]
                                        ↓            ↓
                                        └──── [Next Candidate] ────→ [Done]
```

### 6.2 Step-by-Step Flow

| Step | User Action | System Response | UI State |
|---|---|---|---|
| 1 | Logs in | Dashboard shows: active jobs count, new candidates since last login, recent activity | Dashboard with activity pulse indicators on updated items |
| 2 | Clicks a job card with "5 new candidates" badge | Navigates to job detail with ranked candidate list | Job page with new candidates highlighted (subtle glow animation) |
| 3 | Scans ranked list | Candidates sorted by AI score, new candidates marked with "New" badge | List with score bars, confidence dots, skill chips preview |
| 4 | Clicks top candidate | Right panel slides in with full profile: score breakdown, explanation, skills, experience | Animated panel with score breakdown chart (radar/bar), explanation text |
| 5 | Reads explanation: "Strong semantic match for distributed systems experience..." | Explanation highlights specific matches between JD and candidate | Key terms highlighted in score explanation |
| 6 | Clicks "Shortlist" status button | Candidate status updates to "Shortlisted", success micro-animation | Status chip animates from "New" to "Shortlisted" with color change |
| 7 | Types a note: "Strong systems design background, schedule for round 2" | Note saved immediately (optimistic update) | Note appears with timestamp, subtle fade-in |
| 8 | Clicks next candidate in list (or uses keyboard ↓) | Panel updates with next candidate's details | Crossfade transition between candidates |
| 9 | Sees a low-confidence candidate | Confidence indicator shows "Low" with explanation: "Limited profile data" | Amber confidence badge with tooltip explaining the low confidence |
| 10 | Clicks "Reject" status button | Candidate status updates, candidate dims in list | Candidate row dims with subtle opacity change, sort position maintained |
| 11 | Repeats for remaining candidates | Progressive review with cumulative status updates | Filter options appear: "Show: All / New / Shortlisted / Rejected" |
| 12 | Filters to "Shortlisted" | List filters to show only shortlisted candidates | Animated filter transition, count badge updates |
| 13 | Done — reviews shortlist | Final shortlist with scores and notes ready for sharing | Export/share option appears in header |

---

## 7. Journey 3: Hiring Manager Evaluation

**Persona**: Marcus Rivera (Hiring Manager)
**Goal**: Review recruiter's shortlist, understand AI reasoning, make decisions
**Time Target**: < 10 minutes for 5-8 candidate evaluation

### 7.1 Flow Diagram

```
[Login] → [Dashboard] → [Select Job] → [View Shortlist]
                                              ↓
                                    [Compare Candidates]
                                    ┌────────┴────────┐
                                    ↓                  ↓
                              [Deep Dive]        [Side-by-Side]
                              [Score Detail]     [Comparison View]
                                    ↓                  ↓
                              [Validate AI]      [Rank Preference]
                                    ↓                  ↓
                                    └──── [Decision] ──┘
                                              ↓
                                     [Add Feedback Note]
```

### 7.2 Step-by-Step Flow

| Step | User Action | System Response | UI State |
|---|---|---|---|
| 1 | Logs in, clicks job with shortlisted candidates | Job page filtered to "Shortlisted" candidates | Clean shortlist view with 5-8 candidates, each showing score and top strength |
| 2 | Clicks "Compare" on top 3 candidates (checkbox select) | Opens comparison view with candidates side-by-side | Side-by-side cards with radar charts showing score dimensions |
| 3 | Reviews semantic scores | Comparison highlights where candidates differ most significantly | Score bars with delta indicators ("+12 vs. Candidate B") |
| 4 | Reads explanation for Candidate A | Detailed explanation panel with specific evidence from profile | Expandable sections: "Strengths", "Gaps", "Confidence Analysis" |
| 5 | Notes that Candidate B has lower semantic but higher experience | Score breakdown makes the trade-off visible | Color-coded dimension comparison makes trade-offs obvious |
| 6 | Clicks "Approve" on Candidate A, "Interview" on Candidate B | Status updates, notifications triggered for recruiter | Status transitions with subtle animation |
| 7 | Adds feedback: "A is strong on architecture. B needs systems design deep-dive in interview." | Notes saved, visible to recruiter | Feedback appears in candidate timeline |

---

## 8. Journey 4: Job Description Editing & Re-Ranking

**Persona**: Sarah Chen (Recruiter)
**Goal**: Refine JD based on hiring manager feedback, see updated rankings
**Time Target**: < 2 minutes from edit to updated rankings

### 8.1 Step-by-Step Flow

| Step | User Action | System Response | UI State |
|---|---|---|---|
| 1 | Opens existing JD, clicks "Edit" | JD form opens in edit mode with current values pre-filled | Edit panel with current values, change tracking |
| 2 | Updates required skills: adds "Kubernetes", removes "Docker Swarm" | Skill chips update in real-time with add/remove animations | Chip animation: new skills fade in green, removed skills fade out red |
| 3 | Updates experience range: 5-10 years → 3-8 years | Range slider updates | Smooth slider interaction |
| 4 | Clicks "Save Changes" | (1) Saves updated JD (2) Regenerates JD embedding (3) Triggers re-ranking of all candidates | Progress indicator: "Updating rankings..." with animated progress |
| 5 | Re-ranking completes (< 10 sec for 100 candidates) | Candidate list re-sorts with updated scores. Changed scores are highlighted. | Candidates animate to new positions. Score changes shown: "↑ 78 → 84" or "↓ 72 → 65" |
| 6 | Reviews new rankings | Score change indicators show which candidates moved up/down | Delta badges on each candidate row |
| 7 | Notices a previously mid-ranked candidate is now #2 | Score explanation updated: "Kubernetes experience now strongly matches updated requirements" | Explanation text reflects the new JD context |

---

## 9. Journey 5: Bulk Candidate Import

**Persona**: Sarah Chen (Recruiter) / Alex Torres (Admin)
**Goal**: Import 50-200 candidates from a CSV file
**Time Target**: < 5 minutes including validation and scoring

### 9.1 Step-by-Step Flow

| Step | User Action | System Response | UI State |
|---|---|---|---|
| 1 | Navigates to job, clicks "Import Candidates" | File upload dialog opens | Drag-and-drop zone with accepted format info |
| 2 | Drags CSV file onto upload zone | File parsed, column mapping preview shown | Column mapper: auto-detected columns on left, AURA fields on right |
| 3 | Reviews column mapping, adjusts if needed | System validates mappings and shows preview of first 5 rows | Preview table with green checkmarks for valid mappings |
| 4 | Clicks "Import" | Batch import begins with progress indicator | Progress bar: "Importing... 23/50 candidates" |
| 5 | Import completes | Summary shown: "45 imported, 3 duplicates skipped, 2 validation errors" | Import report with expandable error details |
| 6 | AI scoring begins automatically | Batch scoring with progress: "Scoring candidates... 12/45" | Progress bar with estimated time remaining |
| 7 | Scoring completes | Full ranked list appears with all 45 new candidates scored | Ranked list populates with cascade animation |

---

## 10. Journey 6: Administrative Configuration

**Persona**: Priya Sharma (Director) / Alex Torres (Admin)
**Goal**: Configure system settings, manage users, set scoring defaults

### 10.1 Step-by-Step Flow

| Step | User Action | System Response | UI State |
|---|---|---|---|
| 1 | Navigates to Settings | Settings page with sections: Profile, Team, Scoring, System | Settings nav with clear section labels |
| 2 | Opens "Team" section | List of team members with roles | User management table with role badges |
| 3 | Invites new recruiter | Email invitation sent, pending user appears in list | "Pending" badge on invited user row |
| 4 | Opens "Scoring Defaults" section | Weight sliders for each scoring dimension | Interactive sliders that update a preview score example in real-time |
| 5 | Adjusts default weights: increases experience to 30%, decreases education to 5% | Preview score recalculates to show impact | Score preview animates to new value, delta shown |
| 6 | Clicks "Save Defaults" | New defaults apply to all future jobs (existing jobs unchanged) | Success confirmation with note: "Existing jobs retain their current weights" |

---

## 11. Acceptance Criteria

| Journey | Criterion | Measurement |
|---|---|---|
| Onboarding | New user sees first ranked candidates within 5 minutes of registration | End-to-end timing test |
| Daily Review | Recruiter can review and status 20 candidates in under 15 minutes | Task completion timing with think-aloud protocol |
| HM Evaluation | Hiring manager can understand score reasoning without any training | Comprehension test: "Why was Candidate A ranked higher than Candidate B?" |
| Re-Ranking | JD edit → updated rankings visible within 10 seconds (100 candidates) | Automated performance test |
| Bulk Import | 200 candidates imported and scored within 5 minutes | End-to-end pipeline timing |
| Admin Config | Scoring weight changes reflect in preview within 200ms | UI interaction latency measurement |

---

## 12. Edge Cases

| Journey | Edge Case | Handling |
|---|---|---|
| Onboarding | User abandons mid-registration | Partial data is not saved. Return to registration page with clean form. |
| Onboarding | User creates JD but adds no candidates | Job appears on dashboard with "0 candidates" and persistent CTA to add candidates. |
| Daily Review | All candidates have very similar scores (within 5 points) | UI flags: "Close scores — manual review recommended." Score differences are emphasized in comparison view. |
| Re-Ranking | JD edit while scoring is in progress | Queue the re-ranking. Show: "A re-ranking is already in progress. Your changes will be applied when it completes." |
| Bulk Import | CSV has unexpected encoding (UTF-16, Windows-1252) | Auto-detect encoding. If ambiguous, show encoding selector with preview. |
| Bulk Import | CSV has 5,000 rows (exceeds limit) | Show error: "Maximum 500 candidates per import. Please split your file." |
| Admin Config | Admin removes last admin user | Prevent: "At least one admin user is required." Button disabled with tooltip. |

---

## 13. Future Improvements

| Version | Journey Enhancement |
|---|---|
| v1.5 | Email-based onboarding flow with magic link (no password) |
| v1.5 | Guided tour overlay on first login (Loom-style) |
| v2.0 | Collaborative review journey: multiple reviewers on same shortlist |
| v2.0 | Candidate sourcing journey: AI suggests candidates from talent pool for new JDs |
| v3.0 | Conversational search journey: "Show me candidates like our best hire last quarter" |
| v3.0 | Mobile-optimized review journey for on-the-go hiring managers |

---

## 14. References

| Document | Relationship |
|---|---|
| [USER_PERSONAS.md](./USER_PERSONAS.md) | Personas whose goals drive these journeys |
| [PRODUCT_REQUIREMENTS.md](./PRODUCT_REQUIREMENTS.md) | Requirements implemented in these journeys |
| [MVP_SCOPE.md](./MVP_SCOPE.md) | Which journeys are in scope for v1.0 |
| [../06_FRONTEND/PAGE_SPECIFICATIONS.md](../06_FRONTEND/PAGE_SPECIFICATIONS.md) | Page designs implementing these journeys |
| [../06_FRONTEND/UI_STATE_FLOW.md](../06_FRONTEND/UI_STATE_FLOW.md) | State machines powering journey transitions |
| [../06_FRONTEND/ANIMATION_GUIDE.md](../06_FRONTEND/ANIMATION_GUIDE.md) | Animation specifications for journey micro-interactions |
| [../05_BACKEND/API_SPECIFICATION.md](../05_BACKEND/API_SPECIFICATION.md) | API endpoints backing each journey step |

---

## 15. Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-07-02 | AURA Engineering | Initial user journey maps |
