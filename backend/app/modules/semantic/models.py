# Database table schemas for Semantic Intelligence module caching

CREATE_SEMANTIC_JOB_EMBEDDINGS_TABLE = """
CREATE TABLE IF NOT EXISTS semantic_job_embeddings (
    job_id TEXT PRIMARY KEY,
    embedding BLOB NOT NULL,
    created_at TEXT NOT NULL
);
"""

CREATE_SEMANTIC_MATCHES_TABLE = """
CREATE TABLE IF NOT EXISTS semantic_matches (
    candidate_id TEXT,
    job_id TEXT,
    score REAL NOT NULL,
    PRIMARY KEY (candidate_id, job_id)
);
"""

CREATE_SEMANTIC_MATCHES_INDEX = "CREATE INDEX IF NOT EXISTS idx_semantic_matches_job_id ON semantic_matches(job_id);"
