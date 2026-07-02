# API Specification Document — AURA AI

All endpoints prefix: `/api/v1`

---

## 1. Candidate Intelligence Module

### 1.1 Sourcing dataset ingestion
*   **Method:** `POST`
*   **Route:** `/candidates/upload`
*   **Purpose:** Streams a raw candidate `.jsonl` or `.jsonl.gz` file and loads it into database.
*   **Response (202 Accepted):**
    ```json
    {
      "detail": "Ingestion task started in background."
    }
    ```

---

## 2. Recruiter Intelligence Module

### 2.1 DOCX Job Upload
*   **Method:** `POST`
*   **Route:** `/jobs/upload`
*   **Purpose:** Uploads a DOCX job description, runs heuristic parsing, and stores it as the active job.
*   **Response (201 Created):**
    ```json
    {
      "id": "JOB_UUID",
      "title": "Software Engineer",
      "required_skills": ["Python", "SQL"],
      "preferred_skills": ["Docker"],
      "min_experience": 3.0,
      "seniority": "mid",
      "employment_type": "full-time",
      "industry": "Technology",
      "soft_skills": ["Communication"]
    }
    ```

---

## 3. Semantic Intelligence Module

### 3.1 Retrieve similarity matches
*   **Method:** `GET`
*   **Route:** `/semantic/top`
*   **Purpose:** Computes similarity embeddings and returns the top matches relative to the active job description.
*   **Response (200 OK):**
    ```json
    {
      "job_id": "JOB_UUID",
      "matches": [
        {
          "candidate_id": "CAND001",
          "score": 87.42
        }
      ]
    }
    ```

---

## 4. Feature Intelligence Module

### 4.1 Get Top Feature candidates
*   **Method:** `GET`
*   **Route:** `/features/top`
*   **Purpose:** Returns top candidates grouped by Skills, Experience, Education, and Behavior categories.
*   **Response (200 OK):**
    ```json
    {
      "job_id": "JOB_UUID",
      "job_title": "Software Engineer",
      "skills": [{"candidate_id": "CAND001", "name": "...", "title": "...", "score": 98.0}],
      "experience": [],
      "education": [],
      "behavior": []
    }
    ```

---

## 5. Hybrid Ranking Module

### 5.1 Rebuild Ranking Cache
*   **Method:** `POST`
*   **Route:** `/ranking/build`
*   **Purpose:** Triggers asynchronous cache recalculation for the given weight profile.
*   **Response (202 Accepted):**
    ```json
    {
      "detail": "Ranking cache rebuild started for profile 'generic'."
    }
    ```

---

## 6. Submission Engine (Export)

### 6.1 Download Submission CSV
*   **Method:** `GET`
*   **Route:** `/export/csv`
*   **Purpose:** Generates and returns the official Hack2Skill submission CSV.
*   **Response Headers:**
    *   `Content-Type: text/csv`
    *   `X-Checksum-SHA256: 64-character-hash`
    *   `X-Candidate-Count: 100`
