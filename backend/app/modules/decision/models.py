from app.shared.database.connection import get_db_connection

def create_decision_cache_tables():
    """Create the SQLite tables for decision cache."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS decision_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                profile TEXT NOT NULL,
                rank INTEGER NOT NULL,
                overall_score REAL NOT NULL,
                recommendation TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_level TEXT NOT NULL,
                reason_codes TEXT NOT NULL,
                strengths TEXT NOT NULL,
                gaps TEXT NOT NULL,
                next_action TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_decision_cache_candidate_id ON decision_cache (candidate_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_decision_cache_profile ON decision_cache (profile)')
