# SQL statement schemas for Jobs module tables and indexes

CREATE_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    required_skills TEXT NOT NULL, -- JSON array
    preferred_skills TEXT NOT NULL, -- JSON array
    min_experience REAL NOT NULL,
    seniority TEXT NOT NULL,
    industry TEXT NOT NULL,
    employment_type TEXT NOT NULL,
    soft_skills TEXT NOT NULL, -- JSON array
    created_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 0,
    hiring_profile TEXT, -- JSON structure of Hiring Profile
    upload_metadata TEXT -- JSON structure of Upload Metadata
);
"""

CREATE_JOBS_INDEX = "CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active);"

ALTER_JOBS_PROFILE = "ALTER TABLE jobs ADD COLUMN hiring_profile TEXT;"
ALTER_JOBS_METADATA = "ALTER TABLE jobs ADD COLUMN upload_metadata TEXT;"
