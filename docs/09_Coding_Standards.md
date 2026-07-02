# Coding Standards Document — AURA AI

## 1. Python Style Guidelines
*   **Conformance:** Code must strictly comply with **PEP 8** standards.
*   **Formatter:** Black or Autopep8 with 100 character max line length limit.
*   **Type Hinting:** Mandatory on all service method arguments and return signatures to ensure code clarity.
*   **Docstrings:** Google format docstrings on classes and methods.

---

## 2. Naming Conventions
*   **Variables/Functions:** `snake_case` (e.g. `calculate_overall_score`).
*   **Classes:** `PascalCase` (e.g. `FeatureService`).
*   **Constants:** `UPPER_CASE` (e.g. `DEFAULT_PROFILE`).
*   **Tables:** `snake_case` plural (e.g. `candidates`).

---

## 3. Engineering & Clean Architecture Principles
*   **S: Single Responsibility:** Each module has exactly one job (e.g. `validator.py` only validates).
*   **O: Open/Closed:** Feature engines inherit from `BaseFeatureEngine` allowing easy addition of new metrics without modifying existing classes.
*   **L: Liskov Substitution:** All subclasses of `BaseFeatureEngine` must be drop-in swapable.
*   **I: Interface Segregation:** Services must only expose public methods consumed by API controllers.
*   **D: Dependency Inversion:** Routers depend on Service interfaces, not database implementations directly.

---

## 4. Git Workflow
*   **Branching:**
    *   `main` — Protected production branch.
    *   `feature/*` — Sprints development.
    *   `fix/*` — Bug correction branches.
*   **Commits:** Prefix messages with semantic keywords: `feat:`, `fix:`, `chore:`, `test:`.
