# Product Requirements Document

> AURA AI — Product Documentation
> Version: 1.0 | Last Updated: 2026-07-02 | Author: AURA Engineering

---

## 1. Purpose

This document defines the complete functional and non-functional requirements for AURA AI v1.0. It translates the product vision (see [PRODUCT_VISION.md](./PRODUCT_VISION.md)) into specific, testable, implementable requirements that drive engineering, design, and QA decisions.

Every feature, API endpoint, UI component, and AI behavior should trace back to a requirement in this document.

---

## 2. Scope

This document covers:

- Functional requirements organized by feature domain
- Non-functional requirements (performance, security, usability, accessibility)
- Data requirements and constraints
- Integration requirements
- Requirement prioritization using MoSCoW framework

This document does **not** cover implementation details (see [../05_BACKEND/API_SPECIFICATION.md](../05_BACKEND/API_SPECIFICATION.md)), UI design specifics (see [../06_FRONTEND/PAGE_SPECIFICATIONS.md](../06_FRONTEND/PAGE_SPECIFICATIONS.md)), or AI algorithm details (see [../04_AI/AI_PIPELINE.md](../04_AI/AI_PIPELINE.md)).

---

## 3. Business Context

### 3.1 Business Objectives

| ID | Objective | Success Metric |
|---|---|---|
| BO-01 | Reduce recruiter screening time | ≥ 60% reduction in time spent reviewing unqualified candidates |
| BO-02 | Improve candidate quality in shortlists | ≥ 25% improvement in shortlist-to-interview conversion rate |
| BO-03 | Eliminate keyword-bias in screening | Zero qualified candidates rejected solely due to terminology mismatch |
| BO-04 | Provide auditable hiring decisions | 100% of AI-influenced decisions have explainable score breakdowns |
| BO-05 | Deliver enterprise-quality UX | User satisfaction ≥ 4.2/5.0 on SaaS experience benchmarks |

### 3.2 Stakeholders

| Stakeholder | Role | Primary Concern |
|---|---|---|
| Recruiter (Primary User) | Creates JDs, reviews ranked candidates | Speed, accuracy, trust in recommendations |
| Hiring Manager | Reviews shortlists, provides feedback | Quality of candidates, understanding of AI reasoning |
| HR Leadership | Oversees hiring process compliance | Bias mitigation, auditability, regulatory compliance |
| Candidates (Indirect) | Submit applications | Fair evaluation regardless of resume formatting |
| Engineering Team | Builds and maintains the platform | Clear requirements, testable acceptance criteria |

---

## 4. Technical Context

### 4.1 System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                      AURA AI Platform                       │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Frontend    │  │   Backend    │  │   AI Engine       │  │
│  │  (React SPA) │←→│  (FastAPI)   │←→│ (Sentence Trans.) │  │
│  └─────────────┘  └──────┬───────┘  └───────────────────┘  │
│                          │                                   │
│                   ┌──────┴───────┐                           │
│                   │  Database    │                           │
│                   │  (SQLite/PG) │                           │
│                   └──────────────┘                           │
└─────────────────────────────────────────────────────────────┘
         │                                      │
    ┌────┴─────┐                          ┌─────┴──────┐
    │ Browser  │                          │  Future:   │
    │ (User)   │                          │  ATS APIs  │
    └──────────┘                          └────────────┘
```

### 4.2 Technical Constraints

| Constraint | Details |
|---|---|
| Embedding model | Must use Sentence Transformers (all-MiniLM-L6-v2 for MVP, all-mpnet-base-v2 for production) |
| No external AI APIs | All AI processing must be local — no OpenAI, no cloud ML services |
| Single deployment | Frontend and backend deployable as a single unit for MVP |
| Browser support | Chrome 90+, Firefox 88+, Safari 15+, Edge 90+ |
| Python version | 3.10+ |
| Node.js version | 18+ |

---

## 5. Functional Requirements

### 5.1 Authentication & User Management

| ID | Requirement | Priority | Description |
|---|---|---|---|
| FR-AUTH-01 | User Registration | Must | Users can register with email, full name, and password. Password must meet complexity requirements (8+ chars, 1 uppercase, 1 number, 1 special char). |
| FR-AUTH-02 | User Login | Must | Users can log in with email and password. System issues JWT access token (15 min expiry) and refresh token (7 day expiry). |
| FR-AUTH-03 | Token Refresh | Must | System silently refreshes expired access tokens using valid refresh tokens. User sessions persist without re-login. |
| FR-AUTH-04 | Logout | Must | User can log out, which invalidates the current refresh token on the server. |
| FR-AUTH-05 | Role-Based Access | Should | System supports roles: `admin`, `recruiter`, `viewer`. Admins can manage users and system settings. Recruiters can manage jobs and candidates. Viewers can only read. |
| FR-AUTH-06 | Password Reset | Should | Users can request a password reset via email link with a time-limited token (1 hour expiry). |
| FR-AUTH-07 | Session Management | Could | Users can view and invalidate active sessions from their profile. |

### 5.2 Job Description Management

| ID | Requirement | Priority | Description |
|---|---|---|---|
| FR-JD-01 | Create Job Description | Must | Recruiter can create a JD with: title, department, description text, required skills (tags), preferred skills (tags), experience range (min-max years), education level, employment type, location, and salary range. |
| FR-JD-02 | JD Semantic Processing | Must | Upon creation/update, the system automatically: (1) generates a semantic embedding of the JD text, (2) extracts structured features (skills, experience level, seniority), (3) stores the embedding vector for matching. Processing completes within 2 seconds. |
| FR-JD-03 | Edit Job Description | Must | Recruiter can edit any field of an existing JD. Editing triggers re-processing of the semantic embedding and re-ranking of all associated candidates. |
| FR-JD-04 | Delete Job Description | Must | Recruiter can soft-delete a JD. Deleted JDs are hidden from the active view but retained in the database for audit purposes. Associated candidate rankings are preserved. |
| FR-JD-05 | List Job Descriptions | Must | Dashboard displays all active JDs with: title, department, creation date, candidate count, and status (active/paused/closed). Supports sorting by date, title, and candidate count. |
| FR-JD-06 | JD Status Management | Should | JDs can be set to `active`, `paused`, or `closed`. Paused JDs stop accepting new candidates. Closed JDs are archived. |
| FR-JD-07 | JD Templates | Could | System provides pre-built JD templates for common roles (Software Engineer, Product Manager, Data Scientist, etc.) that recruiters can customize. |
| FR-JD-08 | JD Quality Indicator | Should | System analyzes the JD and provides a quality score (0-100) based on completeness, clarity, and specificity. Low-quality JDs receive improvement suggestions. |

### 5.3 Candidate Management

| ID | Requirement | Priority | Description |
|---|---|---|---|
| FR-CAND-01 | Add Candidate to Job | Must | Recruiter can add candidates to a job by entering structured profile data: name, email, skills (tags), total experience (years), current role, current company, education (degree, institution, field), and summary/bio text. |
| FR-CAND-02 | Bulk Candidate Import | Should | Recruiter can import multiple candidates from a CSV file with defined column mapping. System validates data and reports import errors. |
| FR-CAND-03 | Candidate Profile View | Must | Detailed candidate view showing all profile information, AI match score, score breakdown, and explanation. |
| FR-CAND-04 | Edit Candidate | Must | Recruiter can edit any candidate profile field. Editing triggers re-computation of the match score. |
| FR-CAND-05 | Delete Candidate | Must | Recruiter can remove a candidate from a job (soft delete). |
| FR-CAND-06 | Candidate Status | Should | Each candidate has a pipeline status: `new`, `screening`, `shortlisted`, `interviewing`, `offered`, `hired`, `rejected`. Recruiters can move candidates through the pipeline. |
| FR-CAND-07 | Candidate Notes | Should | Recruiters can add freeform notes to any candidate profile. Notes are timestamped and attributed to the author. |
| FR-CAND-08 | Candidate Search | Should | Recruiter can search across all candidates by name, email, skills, or company. Search uses text matching with typeahead suggestions. |

### 5.4 AI Matching & Ranking

| ID | Requirement | Priority | Description |
|---|---|---|---|
| FR-AI-01 | Automatic Ranking | Must | When a candidate is added to a job, the system automatically computes a match score and inserts the candidate into the ranked list. Ranking is visible within 3 seconds of candidate creation. |
| FR-AI-02 | Semantic Score | Must | System computes cosine similarity between the JD embedding and candidate profile embedding. Score is normalized to 0-100 range. |
| FR-AI-03 | Skill Match Score | Must | System computes overlap between JD required/preferred skills and candidate skills. Score accounts for exact matches and semantically similar skills (e.g., "React" ≈ "React.js"). |
| FR-AI-04 | Experience Score | Must | System evaluates candidate experience against JD requirements: years of experience, seniority alignment, and domain relevance. |
| FR-AI-05 | Hybrid Score Computation | Must | System combines semantic score, skill score, experience score, and education score using configurable weights. Default weights: semantic 40%, skills 25%, experience 20%, education 10%, behavioral 5%. |
| FR-AI-06 | Score Explanation | Must | For every ranked candidate, system provides a natural language explanation covering: (1) why the score is what it is, (2) strongest matching dimensions, (3) gaps or concerns, (4) confidence level. |
| FR-AI-07 | Confidence Score | Must | Each match score includes a confidence indicator (high/medium/low) based on data completeness and score distribution analysis. |
| FR-AI-08 | Re-ranking | Must | When a JD is edited, all associated candidates are automatically re-ranked with updated scores and explanations. |
| FR-AI-09 | Score Weight Configuration | Should | Admin/Recruiter can adjust the weight of each scoring dimension (semantic, skills, experience, education, behavioral) per job. Changes trigger re-ranking. |
| FR-AI-10 | Batch Ranking | Must | System can rank up to 500 candidates against a single JD within 30 seconds. |
| FR-AI-11 | Ranking Comparison | Should | Recruiter can compare 2-4 candidates side-by-side with score breakdowns visualized. |

### 5.5 Dashboard & Analytics

| ID | Requirement | Priority | Description |
|---|---|---|---|
| FR-DASH-01 | Overview Dashboard | Must | Landing page shows: total active jobs, total candidates, recent activity feed, and top-ranked candidates across all jobs. |
| FR-DASH-02 | Job Dashboard | Must | Per-job view showing: ranked candidate list with scores, score distribution chart, pipeline stage breakdown, and AI insights. |
| FR-DASH-03 | Score Distribution | Should | Visual chart (histogram or bell curve) showing the distribution of candidate scores for a job. Helps recruiters understand the talent pool quality. |
| FR-DASH-04 | Pipeline Analytics | Could | Funnel visualization showing candidate progression through pipeline stages. Conversion rates between stages. |
| FR-DASH-05 | Activity Timeline | Should | Chronological feed of actions: candidates added, scores computed, status changes, notes added. |

### 5.6 Settings & Configuration

| ID | Requirement | Priority | Description |
|---|---|---|---|
| FR-SET-01 | User Profile | Must | Users can view and edit their name and email. |
| FR-SET-02 | Password Change | Must | Users can change their password from the settings page. |
| FR-SET-03 | Scoring Weights | Should | Global default scoring weights that apply to new jobs. Can be overridden per job. |
| FR-SET-04 | System Theme | Won't (v1) | Dark theme only for v1.0. Light theme planned for v1.5. |
| FR-SET-05 | Notification Preferences | Could | Users can configure email notifications for key events (new candidates, scoring complete, etc.). |

---

## 6. Non-Functional Requirements

### 6.1 Performance

| ID | Requirement | Target | Measurement |
|---|---|---|---|
| NFR-PERF-01 | Initial page load | < 2 seconds | Lighthouse performance score ≥ 90 |
| NFR-PERF-02 | API response time (CRUD) | < 200ms (P95) | Server-side latency measurement |
| NFR-PERF-03 | Single candidate scoring | < 500ms | End-to-end scoring pipeline timing |
| NFR-PERF-04 | Batch scoring (100 candidates) | < 10 seconds | Pipeline timing with batch processing |
| NFR-PERF-05 | UI interaction response | < 100ms | Time from click to visual feedback |
| NFR-PERF-06 | Embedding generation | < 1 second per text | Sentence Transformer inference timing |

### 6.2 Security

| ID | Requirement | Target |
|---|---|---|
| NFR-SEC-01 | Authentication | JWT-based with refresh token rotation |
| NFR-SEC-02 | Password storage | bcrypt with cost factor 12 |
| NFR-SEC-03 | API authorization | Role-based middleware on all endpoints |
| NFR-SEC-04 | Input validation | Pydantic models on all API inputs |
| NFR-SEC-05 | CORS policy | Whitelist-based origin validation |
| NFR-SEC-06 | Rate limiting | 100 requests/minute per user for standard endpoints, 10/minute for AI endpoints |
| NFR-SEC-07 | Data encryption | TLS 1.3 for transit, AES-256 for sensitive data at rest |
| NFR-SEC-08 | SQL injection prevention | Parameterized queries via ORM |

See [../07_SECURITY/SECURITY.md](../07_SECURITY/SECURITY.md) for complete security architecture.

### 6.3 Usability

| ID | Requirement | Target |
|---|---|---|
| NFR-USE-01 | Onboarding time | New user productive within 60 seconds |
| NFR-USE-02 | Navigation depth | Any feature reachable within 3 clicks from dashboard |
| NFR-USE-03 | Error recovery | Clear error messages with actionable recovery steps |
| NFR-USE-04 | Loading states | Skeleton loaders for all async content (no blank screens) |
| NFR-USE-05 | Empty states | Meaningful empty states with CTAs for all list views |
| NFR-USE-06 | Keyboard navigation | All primary actions accessible via keyboard |

### 6.4 Accessibility

| ID | Requirement | Target |
|---|---|---|
| NFR-ACC-01 | WCAG compliance | Level AA |
| NFR-ACC-02 | Screen reader support | All interactive elements have ARIA labels |
| NFR-ACC-03 | Color contrast | Minimum 4.5:1 for normal text, 3:1 for large text |
| NFR-ACC-04 | Focus management | Visible focus indicators on all interactive elements |
| NFR-ACC-05 | Motion sensitivity | Respect `prefers-reduced-motion` media query |

### 6.5 Reliability

| ID | Requirement | Target |
|---|---|---|
| NFR-REL-01 | API availability | 99.5% uptime |
| NFR-REL-02 | Data durability | Zero data loss on standard operations |
| NFR-REL-03 | Graceful degradation | If AI engine fails, CRUD operations continue normally |
| NFR-REL-04 | Error logging | All errors logged with stack traces and request context |

### 6.6 Maintainability

| ID | Requirement | Target |
|---|---|---|
| NFR-MAINT-01 | Code coverage | > 80% backend, > 70% frontend |
| NFR-MAINT-02 | Documentation | All public APIs documented with docstrings |
| NFR-MAINT-03 | Type safety | 100% TypeScript strict mode (frontend), 100% Pydantic models (backend) |
| NFR-MAINT-04 | Linting | Zero lint warnings in CI |
| NFR-MAINT-05 | Dependency management | All dependencies pinned with lock files |

---

## 7. Data Requirements

### 7.1 Job Description Data Model

| Field | Type | Required | Constraints |
|---|---|---|---|
| `id` | UUID | Auto | Primary key |
| `title` | String | Yes | 3-200 characters |
| `department` | String | No | Max 100 characters |
| `description` | Text | Yes | 50-10,000 characters |
| `required_skills` | String[] | Yes | 1-30 skills, each 1-50 characters |
| `preferred_skills` | String[] | No | 0-20 skills |
| `experience_min` | Integer | No | 0-50 years |
| `experience_max` | Integer | No | ≥ experience_min, ≤ 50 |
| `education_level` | Enum | No | `high_school`, `bachelors`, `masters`, `phd`, `any` |
| `employment_type` | Enum | Yes | `full_time`, `part_time`, `contract`, `internship` |
| `location` | String | No | Max 200 characters |
| `salary_min` | Integer | No | ≥ 0 |
| `salary_max` | Integer | No | ≥ salary_min |
| `status` | Enum | Yes | `active`, `paused`, `closed` |
| `embedding_vector` | Float[] | Auto | 384-dimensional (MiniLM) or 768-dimensional (mpnet) |
| `quality_score` | Float | Auto | 0.0-100.0 |
| `created_by` | UUID | Auto | Foreign key to users |
| `created_at` | DateTime | Auto | UTC timestamp |
| `updated_at` | DateTime | Auto | UTC timestamp |

### 7.2 Candidate Data Model

| Field | Type | Required | Constraints |
|---|---|---|---|
| `id` | UUID | Auto | Primary key |
| `job_id` | UUID | Yes | Foreign key to jobs |
| `full_name` | String | Yes | 2-100 characters |
| `email` | String | Yes | Valid email format |
| `phone` | String | No | Valid phone format |
| `skills` | String[] | Yes | 1-50 skills |
| `total_experience` | Float | Yes | 0-50 years |
| `current_role` | String | No | Max 100 characters |
| `current_company` | String | No | Max 100 characters |
| `education_degree` | String | No | Max 100 characters |
| `education_institution` | String | No | Max 200 characters |
| `education_field` | String | No | Max 100 characters |
| `summary` | Text | No | Max 5,000 characters |
| `embedding_vector` | Float[] | Auto | Same dimension as JD embeddings |
| `status` | Enum | Yes | Pipeline status enum |
| `created_at` | DateTime | Auto | UTC timestamp |
| `updated_at` | DateTime | Auto | UTC timestamp |

### 7.3 Match Score Data Model

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | UUID | Auto | Primary key |
| `job_id` | UUID | Yes | Foreign key to jobs |
| `candidate_id` | UUID | Yes | Foreign key to candidates |
| `overall_score` | Float | Yes | 0.0-100.0, final hybrid score |
| `semantic_score` | Float | Yes | 0.0-100.0, cosine similarity component |
| `skill_score` | Float | Yes | 0.0-100.0, skill match component |
| `experience_score` | Float | Yes | 0.0-100.0, experience match component |
| `education_score` | Float | Yes | 0.0-100.0, education match component |
| `behavioral_score` | Float | Yes | 0.0-100.0, behavioral signals component |
| `confidence` | Enum | Yes | `high`, `medium`, `low` |
| `explanation` | Text | Yes | Natural language explanation |
| `score_weights` | JSON | Yes | Weights used for this computation |
| `computed_at` | DateTime | Auto | UTC timestamp |

See [../02_DATA/DATA_DICTIONARY.md](../02_DATA/DATA_DICTIONARY.md) for complete data dictionary.

---

## 8. Acceptance Criteria

### 8.1 Core Flow Acceptance

| Test | Steps | Expected Result |
|---|---|---|
| Create JD and rank candidates | 1. Create a JD for "Senior React Developer" 2. Add 10 candidates with varying profiles 3. View ranked list | All 10 candidates are ranked with scores, explanations, and confidence levels. A candidate with React experience but listing "React.js" (not "React") still ranks in top 3. |
| Score explanation quality | 1. View any ranked candidate 2. Read the explanation | Explanation clearly states which factors contributed positively/negatively and why. Non-technical recruiter can understand the reasoning. |
| Edit JD triggers re-ranking | 1. Edit JD to change required skills 2. View ranked list | All candidates are re-ranked with updated scores. Score changes are visible within 5 seconds. |
| Keyword-game resilience | 1. Create JD for "Machine Learning Engineer" 2. Add candidate A with keyword-stuffed resume (many ML terms, little substance) 3. Add candidate B with genuine ML experience described naturally | Candidate B ranks higher than candidate A due to semantic understanding of genuine expertise vs. keyword stuffing. |

### 8.2 Non-Functional Acceptance

| Test | Method | Pass Criteria |
|---|---|---|
| Performance | Lighthouse audit on deployed frontend | Score ≥ 90 |
| Accessibility | axe-core automated testing | Zero critical/serious violations |
| Security | OWASP top 10 checklist review | All items addressed |
| Responsiveness | Test on 320px, 768px, 1024px, 1440px, 1920px viewports | Fully functional and visually correct at all sizes |

---

## 9. Edge Cases

| Scenario | Handling |
|---|---|
| **JD with contradictory requirements** (e.g., "5 years React, must be entry-level") | System processes as-is but flags conflicting signals in the JD quality indicator. Scoring uses all signals, and explanations may note the inconsistency. |
| **Candidate with 0 skills listed** | System relies entirely on semantic matching from summary/bio text. Skill score defaults to 0. Confidence is set to `low`. Explanation notes the missing structured data. |
| **Duplicate candidate submission** | System detects duplicates by email within the same job. Returns a validation error with a link to the existing candidate profile. |
| **Very long JD (10,000 chars)** | System truncates to model max token length (256/512 tokens depending on model). A warning is logged. The truncation strategy prioritizes the first portion (which typically contains the most important requirements). |
| **Non-English content** | v1.0 uses English-only models. Non-English text may produce low-quality embeddings. System does not block non-English content but displays a warning to the user. |
| **Concurrent edits** | Optimistic concurrency control using `updated_at` timestamps. If a conflict is detected, the second write fails with a conflict error and the user is prompted to refresh and retry. |
| **Empty candidate pool** | Job dashboard shows a professional empty state with a CTA to add candidates. Score distribution chart shows an empty state message. |

---

## 10. Future Improvements

| Version | Feature | Business Value |
|---|---|---|
| v1.5 | Resume upload with automatic parsing | Eliminates manual data entry, 10x faster candidate creation |
| v1.5 | Email notifications | Keeps recruiters informed without logging in |
| v2.0 | Interview scheduling integration | End-to-end hiring workflow |
| v2.0 | Collaborative evaluation | Multiple stakeholders contribute to hiring decisions |
| v2.0 | Advanced analytics | Data-driven insights on hiring patterns and pipeline health |
| v3.0 | Custom model training | Organization-specific models that improve with hiring outcome data |
| v3.0 | Natural language job search | "Find me backend engineers who've worked at startups" |
| v3.0 | Candidate relationship management | Long-term talent pool management across multiple roles |

---

## 11. References

| Document | Relationship |
|---|---|
| [PRODUCT_VISION.md](./PRODUCT_VISION.md) | Vision and strategic context for these requirements |
| [USER_PERSONAS.md](./USER_PERSONAS.md) | User profiles these requirements serve |
| [USER_JOURNEY.md](./USER_JOURNEY.md) | User flows implementing these requirements |
| [MVP_SCOPE.md](./MVP_SCOPE.md) | Which requirements are in/out for v1.0 |
| [../02_DATA/DATA_DICTIONARY.md](../02_DATA/DATA_DICTIONARY.md) | Complete data field specifications |
| [../03_ARCHITECTURE/SYSTEM_ARCHITECTURE.md](../03_ARCHITECTURE/SYSTEM_ARCHITECTURE.md) | Architecture implementing these requirements |
| [../04_AI/AI_PIPELINE.md](../04_AI/AI_PIPELINE.md) | AI system powering FR-AI requirements |
| [../05_BACKEND/API_SPECIFICATION.md](../05_BACKEND/API_SPECIFICATION.md) | API endpoints implementing these requirements |
| [../06_FRONTEND/PAGE_SPECIFICATIONS.md](../06_FRONTEND/PAGE_SPECIFICATIONS.md) | UI pages implementing these requirements |
| [../07_SECURITY/SECURITY.md](../07_SECURITY/SECURITY.md) | Security requirements implementation |

---

## 12. Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-07-02 | AURA Engineering | Initial product requirements document |
