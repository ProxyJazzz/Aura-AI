# Database Design Document — AURA AI

## 1. Relational Tables
AURA AI uses SQLite (`aura.db` and `export_cache.db`) with active foreign key constraints.

### 1.1 `candidates` Table
Holds processed candidate profiles.
*   `candidate_id` (TEXT, PRIMARY KEY): Unique identifier.
*   `is_valid` (INTEGER): 0 or 1 flag indicating Pydantic validation status.
*   `raw_json` (TEXT): Gzipped candidate JSON data payload.
*   `current_title` (TEXT): Normalized title.
*   `years_of_experience` (REAL): Float value.
*   `location` (TEXT): City/region.
*   `highest_education_tier` (TEXT): `tier_1`, `tier_2`, etc.

### 1.2 `jobs` Table
Holds job description details parsed from DOCX.
*   `id` (TEXT, PRIMARY KEY): Job unique identifier.
*   `title` (TEXT): Title of the position.
*   `raw_text` (TEXT): Full parsed text body.
*   `required_skills` (TEXT): JSON-serialized array of technical keywords.
*   `preferred_skills` (TEXT): JSON-serialized array of Technical keywords.
*   `is_active` (INTEGER): Active flag (only 1 job active at a time).

### 1.3 `export_artifacts` Table (inside `export_cache.db`)
Stores cached generated export files.
*   `export_id` (TEXT, PRIMARY KEY): UUID.
*   `export_type` (TEXT): `csv`, `json`, or `report`.
*   `profile` (TEXT): Scoring weight profile name.
*   `checksum` (TEXT): SHA-256 artifact hash.
*   `blob` (BLOB): File binary content.
*   `created_at` (TEXT): UTC Isoformat string.

---

## 2. Table Indexes
To guarantee fast sorting, pagination, and indexing:
*   `CREATE INDEX IF NOT EXISTS idx_candidates_is_valid ON candidates(is_valid);`
*   `CREATE INDEX IF NOT EXISTS idx_candidates_experience ON candidates(years_of_experience);`
*   `CREATE INDEX IF NOT EXISTS idx_export_type ON export_artifacts(export_type);`
*   `CREATE INDEX IF NOT EXISTS idx_export_profile ON export_artifacts(profile);`

---

## 3. SQLite Configurations & Thread-Safety
AURA AI enforces the following PRAGMAs to optimize for high-speed writes and concurrent read isolation:
*   `PRAGMA journal_mode=WAL;` — Enables Write-Ahead Logging for non-blocking concurrent reads and writes.
*   `PRAGMA synchronous=NORMAL;` — Balances safety and transaction speed.
*   `PRAGMA foreign_keys=ON;` — Enforces database-level cascading integrity constraints.
*   Connection Timeout is configured to `30.0` seconds to prevent SQL lock errors during heavy write batches.
