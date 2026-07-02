# Testing Strategy Document — AURA AI

## 1. Testing Pyramid
AURA AI enforces a three-tiered testing strategy:
1.  **Unit Tests (80% coverage):** Validates separate calculations inside candidate Pydantic validation rules, DOCX job parsers, specific feature dimension engines, and exporters.
2.  **Integration Tests:** Uses FastAPI's `TestClient` to verify router mappings, database connection transactions, and cache persistence lifecycle.
3.  **Performance/Load Benchmarks:** Tests high-volume datasets (e.g. 100,000 candidates) against timing goals.

---

## 2. Frameworks & Tools
*   **Engine:** `pytest` (v9.1+).
*   **Libraries:** `pytest-asyncio` for async controller testing.
*   **API Tests:** `fastapi.testclient.TestClient`.
*   **Diagnostics:** `psutil` (for tracking RAM and peak CPU load during large-scale scoring batches).

---

## 3. Mocking Strategy
*   **Upstream Services:** Avoid live calls to models or databases during unit engine checks by mocking `CandidateService` and `JobService` interfaces.
*   **Network Isolation:** Force Hugging Face offline settings during testing:
    `TRANSFORMERS_OFFLINE=1`  
    `HF_HUB_OFFLINE=1`

---

## 4. Performance Assertions
Every release check must execute the large-scale benchmark and verify:
*   Ingestion time for 1,000 profiles < 1.0s.
*   Sorting and exporting top 100 candidates out of 100,000 < 2.0s.
