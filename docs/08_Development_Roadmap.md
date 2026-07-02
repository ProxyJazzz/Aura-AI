# Development Roadmap Document — AURA AI

## 1. Project Phase Breakdown

### Phase 1: Foundation (Sprint 1)
*   **Goal:** Establish workspace boilerplate, standard database migrations, loggers, exceptions, and settings configurations.
*   **Deliverables:** Pydantic environment configurations, logging setup, SQLite connection pooling class.
*   **Success Criteria:** Application boots and tests pass.

### Phase 2: Candidate Intelligence (Sprint 2)
*   **Goal:** Construct Candidate loading ETL pipelines.
*   **Deliverables:** Stream processing script for jsonl candidate databases, candidate repository methods.
*   **Success Criteria:** Successfully parsed 10,000+ candidates into SQLite without CPU exhaustion.

### Phase 3: Recruiter Intelligence (Sprint 3)
*   **Goal:** Build Job description extraction engine.
*   **Deliverables:** Word DOCX parser service, active Job lookup and update mechanisms.
*   **Success Criteria:** Extraction accuracy of required technical skills > 90%.

### Phase 4: Semantic Intelligence (Sprint 4)
*   **Goal:** Integrate semantic similarity logic.
*   **Deliverables:** SentenceTransformer model wrapper, NumPy dot product scoring calculations.
*   **Success Criteria:** Semantic index correctly returns sorted lists on 100k candidate vectors under 1.5 seconds.

### Phase 5: Feature Intelligence (Sprint 5)
*   **Goal:** Orchestrate 6 score scorecard engines.
*   **Deliverables:** Engine calculations (Skill, Exp, Edu, Cert, Lang, Behavior) inheriting from `BaseFeatureEngine`.
*   **Success Criteria:** Pre-cached JSON scorecards successfully persist on disk.

### Phase 6: Hybrid Ranking (Sprint 6)
*   **Goal:** Perform weighted scoring and deterministic tie-breaking.
*   **Deliverables:** Configurable weights loader, ranking endpoints, caching table mechanisms.
*   **Success Criteria:** Sorting is perfectly deterministic for tie scores.

### Phase 7: Decision Intelligence (Sprint 7)
*   **Goal:** Produce recruiter recommendations and reason metrics.
*   **Deliverables:** Decision mapping, confidence calculation logic.
*   **Success Criteria:** Recruiter-ready text generated for every top candidate.

### Phase 8: Recruiter Dashboard (Sprint 8)
*   **Goal:** Integrate React client UI.
*   **Deliverables:** CSS variables setup, cards, tables, dashboard pages.
*   **Success Criteria:** Render loading speeds < 100ms.

### Phase 9: Analytics (Sprint 9)
*   **Goal:** Provide aggregate data metrics.
*   **Deliverables:** Score distribution bucket calculations, avg score analytics endpoint.
*   **Success Criteria:** Charts draw data from the correct `/analytics` endpoint.

### Phase 10: Submission Engine (Sprint 10)
*   **Goal:** Finalize export files generation and validations.
*   **Deliverables:** CSV, JSON report exporters, validation ruleset.
*   **Success Criteria:** End-to-end export duration for top-100 candidates < 2 seconds.

### Phase 11: Deployment (Sprint 11)
*   **Goal:** Release application on cloud hosting platforms.
*   **Deliverables:** Render blueprint deployment configurations (`render.yaml`).
*   **Success Criteria:** Operational checks return active status.
