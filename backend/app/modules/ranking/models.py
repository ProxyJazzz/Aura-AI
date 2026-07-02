from loguru import logger
from app.shared.database.connection import get_db_connection

def create_ranking_cache_tables():
    """Create the SQLite tables for ranking cache."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ranking_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                profile TEXT NOT NULL,
                overall_score REAL NOT NULL,
                semantic_score REAL NOT NULL,
                skill_score REAL NOT NULL,
                experience_score REAL NOT NULL,
                education_score REAL NOT NULL,
                certification_score REAL NOT NULL,
                language_score REAL NOT NULL,
                behavior_score REAL NOT NULL,
                decision TEXT,
                confidence REAL,
                recommendation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_ranking_cache_candidate_id ON ranking_cache (candidate_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_ranking_cache_profile ON ranking_cache (profile)')
