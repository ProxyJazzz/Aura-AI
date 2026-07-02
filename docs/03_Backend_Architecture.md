# Backend Architecture Document — AURA AI

## 1. Intended Folder Structure
```
backend/
├── app/
│   ├── config/             # Weight configurations
│   ├── core/               # App lifespans, router mounts, setting loaders
│   ├── modules/            # Domain Modules
│   │   ├── candidates/     # Candidate ETL, validation, repository
│   │   ├── jobs/           # DOCX Job parser, extraction, repository
│   │   ├── semantic/       # Embedding generations and dot similarity
│   │   ├── features/       # 6 Scoring dimensions engines
│   │   ├── ranking/        # Hybrid ranking aggregation
│   │   ├── export/         # Validator, CSV/JSON/report exporters
│   │   └── health/         # System diagnostic status checks
│   └── shared/             # Shared DB, global exceptions, request logging middleware
├── tests/                  # Pytest validation suites
└── requirements.txt        # Production Python dependencies list
```

---

## 2. Layer Responsibilities
*   **API Router Layer (`api.py`):** Acts as the controller. Performs request body validation using Pydantic, maps endpoints to service calls, and translates domain errors to HTTP exceptions.
*   **Service Layer (`service.py`):** Holds the domain business rules. Orchestrates model loading, caches intermediate scores, and maps repositories.
*   **Repository Layer (`repository.py`):** Isolates database connectivity and raw SQL queries. Deals directly with connection cursors and transaction contexts.

---

## 3. Dependency Injection
AURA AI uses Python's standard module-import boundaries for static dependency registration. Services expose class methods or singletons directly to routers, which prevents instantiation overhead and keeps testing straightforward with `unittest.mock.patch`.

---

## 4. Exception Handling
All custom domain exceptions derive from `AuraBaseError`. A unified global exception handler registered in `app/core/main.py` intercepts these errors and maps them to clean, JSON-formatted HTTP error envelopes:
```json
{
  "detail": "Descriptive message detailing the validation or processing failure."
}
```
*   `ValidationError` maps to `422 Unprocessable Entity`.
*   `NotFoundError` maps to `404 Not Found`.
*   `ConflictError` maps to `409 Conflict`.
