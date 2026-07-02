import json
from typing import Optional, Dict, Any
from app.shared.database import get_db_connection

class CandidateCache:
    """Manages SQLite-based caching for Candidate Intelligence statistics and metadata."""

    @staticmethod
    def get_statistics() -> Optional[Dict[str, Any]]:
        """Retrieve cached statistics from SQLite dataset_statistics table."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM dataset_statistics WHERE key = 'summary_stats';"
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None

    @staticmethod
    def save_statistics(stats: Dict[str, Any]) -> None:
        """Cache compiled statistics into SQLite dataset_statistics table."""
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO dataset_statistics (key, value)
                VALUES ('summary_stats', ?);
                """,
                (json.dumps(stats),),
            )

    @staticmethod
    def clear() -> None:
        """Clear cached statistics."""
        with get_db_connection() as conn:
            conn.execute("DELETE FROM dataset_statistics WHERE key = 'summary_stats';")
