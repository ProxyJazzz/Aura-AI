# Database table schemas and index creation SQL statements for Candidates module

CREATE_CANDIDATES_TABLE = """
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id TEXT PRIMARY KEY,
    is_valid INTEGER NOT NULL,
    is_honeypot INTEGER NOT NULL,
    validation_error TEXT,
    raw_json TEXT NOT NULL,
    
    -- Extracted Features
    anonymized_name TEXT,
    location TEXT,
    country TEXT,
    years_of_experience REAL,
    current_title TEXT,
    current_company TEXT,
    profile_completeness_score REAL,
    recruiter_response_rate REAL,
    avg_response_time_hours REAL,
    open_to_work_flag INTEGER,
    skills_list TEXT,
    primary_skills_count INTEGER,
    has_ai_ml_skills INTEGER,
    has_only_consulting_experience INTEGER,
    has_worked_in_consulting INTEGER,
    num_companies INTEGER,
    avg_tenure_months REAL,
    highest_education_tier TEXT,
    has_masters_or_phd INTEGER,
    num_certifications INTEGER,
    num_languages INTEGER,
    last_active_date TEXT
);
"""

CREATE_STATISTICS_TABLE = """
CREATE TABLE IF NOT EXISTS dataset_statistics (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

INDEX_QUERIES = [
    "CREATE INDEX IF NOT EXISTS idx_candidates_is_valid ON candidates(is_valid);",
    "CREATE INDEX IF NOT EXISTS idx_candidates_is_honeypot ON candidates(is_honeypot);",
    "CREATE INDEX IF NOT EXISTS idx_candidates_experience ON candidates(years_of_experience);",
    "CREATE INDEX IF NOT EXISTS idx_candidates_open_to_work ON candidates(open_to_work_flag);",
    "CREATE INDEX IF NOT EXISTS idx_candidates_location ON candidates(location);",
    "CREATE INDEX IF NOT EXISTS idx_candidates_skills ON candidates(skills_list);"
]
