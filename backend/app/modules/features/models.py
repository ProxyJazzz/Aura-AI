# Database table schemas for Feature Intelligence module caching

CREATE_FEATURE_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS feature_profiles (
    candidate_id TEXT PRIMARY KEY,
    semantic_score REAL NOT NULL,
    skill_score REAL NOT NULL,
    experience_score REAL NOT NULL,
    education_score REAL NOT NULL,
    certification_score REAL NOT NULL,
    language_score REAL NOT NULL,
    behavior_score REAL NOT NULL,
    feature_vector TEXT NOT NULL,  -- JSON list
    metadata TEXT NOT NULL,        -- JSON object
    created_at TEXT NOT NULL
);
"""
