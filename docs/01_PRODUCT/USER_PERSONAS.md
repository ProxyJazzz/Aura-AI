# User Personas

> AURA AI — Product Documentation
> Version: 1.0 | Last Updated: 2026-07-02 | Author: AURA Engineering

---

## 1. Purpose

This document defines the target user personas for AURA AI. Each persona represents a distinct user archetype with specific goals, frustrations, behaviors, and technical proficiency levels. These personas drive design decisions, feature prioritization, and UX writing throughout the platform.

Every UI decision, feature scope, and communication tone should be validated against these personas.

---

## 2. Scope

This document covers:

- Primary personas (direct users of the platform)
- Secondary personas (stakeholders who consume outputs)
- Persona demographics, behaviors, goals, and pain points
- Technical proficiency mapping
- Persona-to-feature mapping

This document does **not** cover user flows (see [USER_JOURNEY.md](./USER_JOURNEY.md)) or page-level UI specifications (see [../06_FRONTEND/PAGE_SPECIFICATIONS.md](../06_FRONTEND/PAGE_SPECIFICATIONS.md)).

---

## 3. Business Context

AURA AI targets mid-to-large organizations (50-5,000+ employees) with dedicated recruitment functions. The buying decision is typically made by HR leadership, but day-to-day usage is driven by recruiters. The platform must satisfy both the operational needs of daily users and the strategic needs of decision-makers.

### 3.1 User Segments

| Segment | Organization Size | Hiring Volume | Typical ATS | AURA Value Proposition |
|---|---|---|---|---|
| Growth-stage startups | 50-200 employees | 5-20 roles/month | Lever, Ashby | Speed and quality — find the right people fast without a large recruiting team |
| Mid-market | 200-2,000 employees | 20-100 roles/month | Greenhouse, Workday | Scale screening without sacrificing quality or adding headcount |
| Enterprise | 2,000+ employees | 100+ roles/month | Workday, SuccessFactors | Compliance, auditability, and consistent evaluation standards |

---

## 4. Technical Context

Persona definitions inform the technical requirements for:

- **Frontend complexity**: How much flexibility vs. simplicity the UI should offer
- **AI explainability depth**: How technical explanations can be vs. how simplified they need to be
- **Onboarding flow**: How much hand-holding vs. self-service the system needs
- **API surface**: Whether non-UI access (API, CSV export) is needed

---

## 5. Primary Personas

### 5.1 Persona 1: Sarah Chen — The Tech Recruiter

```
┌─────────────────────────────────────────────────────────────┐
│  SARAH CHEN                                                  │
│  Senior Technical Recruiter · Series B Startup · 6 YoE      │
│                                                              │
│  "I spend more time fighting our ATS than actually talking   │
│   to candidates."                                            │
└─────────────────────────────────────────────────────────────┘
```

| Attribute | Detail |
|---|---|
| **Age** | 31 |
| **Role** | Senior Technical Recruiter |
| **Company** | Series B fintech startup, 180 employees |
| **Team Size** | 3-person recruiting team |
| **Hiring Volume** | 8-12 technical roles per month |
| **Technical Proficiency** | Medium — comfortable with SaaS tools, not a developer |
| **Current ATS** | Lever (migrating from spreadsheets) |

#### Goals
1. Quickly identify the top 10-15 candidates from 100+ applicants per role
2. Spend less time on initial screening and more time on relationship building
3. Present well-justified shortlists to hiring managers
4. Keep the hiring pipeline organized and visible

#### Frustrations
1. Current ATS keyword search misses strong candidates who describe their skills differently
2. Manually reviewing 100+ resumes per role takes 2-3 full days
3. Hiring managers question her shortlists: "Why this person and not that one?"
4. No way to explain or defend screening decisions systematically
5. Context-switching between spreadsheets, ATS, and email

#### Behaviors
- Reviews candidates in batches, typically 20-30 at a time
- Uses multiple browser tabs to cross-reference LinkedIn profiles
- Takes notes in a separate doc, then copies into ATS
- Works primarily on a 15" MacBook Pro, occasionally iPad
- Most productive in morning hours (8-11am)

#### AURA AI Value
- **Semantic matching** eliminates the keyword problem that causes her to miss good candidates
- **Ranked lists with explanations** give her confidence in shortlists
- **Score breakdowns** arm her with data when presenting to hiring managers
- **Batch processing** turns a 3-day screening task into a 30-minute review

#### Feature Priorities
| Priority | Features |
|---|---|
| Must | Ranked candidate list, score explanations, JD creation, candidate management |
| High | Side-by-side comparison, batch import, activity timeline |
| Medium | Pipeline management, notes, search |
| Low | Analytics dashboard, templates |

---

### 5.2 Persona 2: Marcus Rivera — The Hiring Manager

```
┌─────────────────────────────────────────────────────────────┐
│  MARCUS RIVERA                                               │
│  VP of Engineering · SaaS Company · 14 YoE                  │
│                                                              │
│  "I need to trust the shortlist. If I can't see the         │
│   reasoning, I'm going to review every resume myself."       │
└─────────────────────────────────────────────────────────────┘
```

| Attribute | Detail |
|---|---|
| **Age** | 38 |
| **Role** | VP of Engineering |
| **Company** | B2B SaaS company, 600 employees |
| **Team Size** | 45 engineers across 6 teams |
| **Hiring Volume** | Involved in 4-6 hires per quarter |
| **Technical Proficiency** | High — former software engineer, understands ML concepts |
| **Current ATS** | Greenhouse (used passively, mostly reviews what recruiters send) |

#### Goals
1. Review a curated shortlist of 5-8 candidates, not 50+
2. Understand **why** each candidate was recommended
3. Ensure technical skills are accurately assessed (not just keyword matches)
4. Spend minimal time in the hiring tool — he has a team to manage
5. Trust the AI enough to delegate initial screening entirely

#### Frustrations
1. Recruiter shortlists often include candidates who don't meet basic technical requirements
2. No visibility into how candidates were screened or filtered
3. ATS shows a "match percentage" but can't explain what it means
4. Reviewing bad shortlists wastes 3-4 hours per week
5. Can't easily compare two candidates' strengths and weaknesses

#### Behaviors
- Reviews candidates in 15-20 minute sessions between meetings
- Focuses on technical skills, system design experience, and career trajectory
- Makes quick decisions — if the data is clear, he acts immediately
- Uses desktop primarily, large monitor
- Skeptical of AI claims — wants to see the reasoning before trusting

#### AURA AI Value
- **Transparent score breakdowns** let him understand and trust the AI's reasoning
- **Dimension-level scores** (semantic, skills, experience) map to how he evaluates candidates mentally
- **Comparison view** enables rapid side-by-side evaluation
- **Confidence indicators** tell him when to trust the score vs. when to dig deeper

#### Feature Priorities
| Priority | Features |
|---|---|
| Must | Score explanations, score breakdown visualization, comparison view |
| High | Candidate detail view with highlighting, confidence indicators |
| Medium | Pipeline status management, notes |
| Low | JD creation, candidate import, admin settings |

---

### 5.3 Persona 3: Priya Sharma — The HR Director

```
┌─────────────────────────────────────────────────────────────┐
│  PRIYA SHARMA                                                │
│  Director of Talent Acquisition · Enterprise · 12 YoE       │
│                                                              │
│  "I need to prove to the board that our hiring process is    │
│   both fair and efficient. Gut feelings don't fly anymore."  │
└─────────────────────────────────────────────────────────────┘
```

| Attribute | Detail |
|---|---|
| **Age** | 42 |
| **Role** | Director of Talent Acquisition |
| **Company** | Enterprise software company, 2,500 employees |
| **Team Size** | 12 recruiters reporting to her |
| **Hiring Volume** | 40-60 roles per month across the organization |
| **Technical Proficiency** | Low-Medium — uses SaaS tools daily but not technical |
| **Current ATS** | Workday Recruiting (enterprise-mandated) |

#### Goals
1. Ensure hiring process is compliant with anti-discrimination regulations
2. Reduce time-to-fill without sacrificing quality
3. Standardize evaluation criteria across her team of 12 recruiters
4. Generate reports showing hiring efficiency and diversity metrics
5. Justify the ROI of recruitment technology investments to the CFO

#### Frustrations
1. Each recruiter evaluates candidates differently — no consistency
2. Cannot audit or explain hiring decisions after the fact
3. Current ATS provides vanity metrics, not actionable insights
4. Bias complaints from candidates with no way to demonstrate fairness
5. Board wants data-driven hiring but tools don't provide meaningful data

#### Behaviors
- Monitors dashboards weekly rather than using the tool daily
- Reviews aggregate metrics, not individual candidates
- Needs to export data for board presentations
- Works on a corporate Windows laptop
- Delegates operational tasks but wants strategic visibility

#### AURA AI Value
- **Explainable AI** provides audit trails for every hiring decision
- **Consistent scoring** ensures all candidates are evaluated against the same criteria regardless of which recruiter manages them
- **Analytics dashboard** provides the data she needs for board presentations
- **Configurable weights** let her set organizational standards for evaluation

#### Feature Priorities
| Priority | Features |
|---|---|
| Must | Score explanations (for audit), analytics overview, user management |
| High | Export functionality, pipeline analytics, scoring weight configuration |
| Medium | Activity timeline, team performance metrics |
| Low | Individual candidate management, JD creation |

---

## 6. Secondary Personas

### 6.1 Persona 4: Alex Torres — The System Administrator

```
┌─────────────────────────────────────────────────────────────┐
│  ALEX TORRES                                                 │
│  HR Technology Analyst · Mid-Market · 4 YoE                 │
│                                                              │
│  "If I can't deploy it in an afternoon and it doesn't have  │
│   an API, I'm not interested."                               │
└─────────────────────────────────────────────────────────────┘
```

| Attribute | Detail |
|---|---|
| **Age** | 28 |
| **Role** | HR Technology Analyst / HRIS Administrator |
| **Technical Proficiency** | High — comfortable with APIs, configuration, and basic scripting |
| **Primary Tasks** | System setup, user management, data import/export, troubleshooting |

#### Goals
1. Deploy AURA AI quickly with minimal configuration
2. Integrate with existing tools (ATS, HRIS) via API
3. Manage users and permissions efficiently
4. Import existing candidate data from CSV/other systems

#### Feature Priorities
| Priority | Features |
|---|---|
| Must | User management, CSV import, clear error messages |
| High | API documentation, system health status |
| Medium | Configuration management, audit logs |

---

### 6.2 Persona 5: Jordan Williams — The Candidate (Indirect)

```
┌─────────────────────────────────────────────────────────────┐
│  JORDAN WILLIAMS                                             │
│  Senior Software Engineer · Job Seeker · 8 YoE              │
│                                                              │
│  "I'm tired of tailoring my resume to keyword-match every   │
│   job posting. My work should speak for itself."             │
└─────────────────────────────────────────────────────────────┘
```

| Attribute | Detail |
|---|---|
| **Age** | 33 |
| **Role** | Senior Software Engineer (job seeker) |
| **Technical Proficiency** | Very high |
| **Relationship to AURA** | Indirect — never uses the UI, benefits from fair evaluation |

#### Goals
1. Be evaluated on actual qualifications, not resume formatting
2. Get considered for roles even when using different terminology
3. Have career trajectory and growth recognized, not just keyword counts

#### Impact on Design
- Jordan never uses AURA directly, but her existence justifies the entire semantic approach
- The AI must genuinely understand that "built and shipped React applications serving 10M users" is more valuable than a resume listing "React" 15 times
- Scoring explanations should reflect this understanding

---

## 7. Persona-to-Feature Matrix

| Feature | Sarah (Recruiter) | Marcus (HM) | Priya (Director) | Alex (Admin) |
|---|---|---|---|---|
| JD Creation & Management | ★★★ Primary user | ★ Reviews | ★ Monitors | ★ Setup |
| Candidate Management | ★★★ Primary user | ★★ Reviews shortlist | ★ Monitors | ★★ Imports |
| AI Ranking & Scores | ★★★ Daily use | ★★★ Decision basis | ★★ Audit trail | ★ Validates |
| Score Explanations | ★★★ Presents to HM | ★★★ Trust basis | ★★★ Compliance | ★ Tests |
| Comparison View | ★★ Uses for shortlisting | ★★★ Primary tool | ★ Occasional | — |
| Dashboard Overview | ★★★ Daily hub | ★ Quick check | ★★★ Weekly review | ★ Health check |
| Analytics | ★★ Pipeline tracking | ★ Occasional | ★★★ Board reports | ★ System metrics |
| User Management | — | — | ★★ Team management | ★★★ Primary duty |
| Settings & Config | ★ Own profile | ★ Own profile | ★★ Org settings | ★★★ System config |
| CSV Import/Export | ★★ Imports candidates | — | ★★ Exports reports | ★★★ Data migration |

*Rating: ★★★ = Critical, ★★ = Important, ★ = Occasional, — = Not relevant*

---

## 8. Acceptance Criteria

| Criterion | Validation Method |
|---|---|
| Sarah can create a JD and review ranked candidates within 5 minutes of first login | Usability test with recruiter participants |
| Marcus can understand a candidate's score breakdown without any training | Comprehension test — show score UI, ask "why was this candidate ranked #3?" |
| Priya can explain the AI scoring methodology to her board using only AURA's output | Explainability audit — can the explanations stand alone in a presentation? |
| Alex can deploy AURA and create the first user within 30 minutes | Deployment test on clean machine following documentation only |
| Jordan-type candidates (natural language, no keyword stuffing) rank higher than keyword-stuffed profiles | Automated regression test with controlled test data |

---

## 9. Edge Cases

| Edge Case | Persona Impact | Handling |
|---|---|---|
| Recruiter with no technical knowledge evaluating engineering roles | Sarah | Score explanations must avoid jargon. "Strong match on distributed systems experience" not "High cosine similarity on systems architecture embedding subspace." |
| Hiring manager who distrusts AI | Marcus | Comparison view and transparent scoring let him verify independently. System earns trust, doesn't demand it. |
| Director audited by legal for hiring discrimination | Priya | Complete audit trail: every score, every weight, every explanation is timestamped and immutable. |
| Admin importing 10,000 candidates from legacy system | Alex | Batch import with progress indicator, validation report, and rollback capability. |
| Candidate who is a career changer (teacher → developer) | Jordan | Semantic matching recognizes transferable skills and explains the match despite unconventional background. |

---

## 10. Future Improvements

| Version | Persona Enhancement |
|---|---|
| v1.5 | **Sarah**: Slack/Teams notifications for new candidate scores |
| v1.5 | **Marcus**: Calendar integration for interview scheduling directly from shortlist |
| v2.0 | **Priya**: Diversity and equity analytics dashboard |
| v2.0 | **Alex**: SSO integration (SAML 2.0, OIDC) for enterprise deployment |
| v2.0 | **Jordan**: Candidate portal where they can see their profile and how they're being evaluated |
| v3.0 | **Sarah**: AI assistant that drafts outreach messages based on candidate profiles |
| v3.0 | **Marcus**: Predictive hiring success scores based on historical data |

---

## 11. References

| Document | Relationship |
|---|---|
| [PRODUCT_VISION.md](./PRODUCT_VISION.md) | Strategic context these personas support |
| [PRODUCT_REQUIREMENTS.md](./PRODUCT_REQUIREMENTS.md) | Requirements derived from persona needs |
| [USER_JOURNEY.md](./USER_JOURNEY.md) | User flows for each persona |
| [MVP_SCOPE.md](./MVP_SCOPE.md) | Which persona needs are addressed in v1.0 |
| [../06_FRONTEND/DESIGN_SYSTEM.md](../06_FRONTEND/DESIGN_SYSTEM.md) | Design system informed by persona proficiency levels |
| [../06_FRONTEND/PAGE_SPECIFICATIONS.md](../06_FRONTEND/PAGE_SPECIFICATIONS.md) | Page designs optimized for primary personas |

---

## 12. Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-07-02 | AURA Engineering | Initial persona definitions |
