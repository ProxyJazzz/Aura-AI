from typing import List, Optional, Dict, Any
from app.shared.database.connection import get_db_connection
from app.modules.decision.models import create_decision_cache_tables

class DecisionRepository:
    """Handles database operations for Decision cache."""

    @classmethod
    def get_top_decisions(cls, profile: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Fetch top decisions from the cache for a given profile."""
        create_decision_cache_tables()
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM decision_cache 
                WHERE profile = ?
                ORDER BY rank ASC
                LIMIT ? OFFSET ?
            ''', (profile, limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def get_decision(cls, candidate_id: str, profile: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific candidate's decision from the cache."""
        create_decision_cache_tables()
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM decision_cache 
                WHERE candidate_id = ? AND profile = ?
            ''', (candidate_id, profile))
            row = cursor.fetchone()
            return dict(row) if row else None

    @classmethod
    def save_decisions(cls, profile: str, decisions: List[dict]):
        """Save a batch of candidate decisions to the cache, overwriting the old ones for this profile."""
        create_decision_cache_tables()
        with get_db_connection() as conn:
            conn.execute('DELETE FROM decision_cache WHERE profile = ?', (profile,))
            
            if not decisions:
                return
                
            columns = [
                "candidate_id", "profile", "rank", "overall_score", 
                "recommendation", "confidence", "risk_level", "reason_codes", 
                "strengths", "gaps", "next_action"
            ]
            
            placeholders = ", ".join(["?"] * len(columns))
            query = f"INSERT INTO decision_cache ({', '.join(columns)}) VALUES ({placeholders})"
            
            data = []
            for d in decisions:
                data.append((
                    d["candidate_id"],
                    profile,
                    d["rank"],
                    d["overall_score"],
                    d["recommendation"],
                    d["confidence"],
                    d["risk_level"],
                    d["reason_codes"],
                    d["strengths"],
                    d["gaps"],
                    d["next_action"]
                ))
                
            conn.executemany(query, data)

    @classmethod
    def clear_cache(cls, profile: Optional[str] = None):
        """Clear cache for a specific profile or all profiles."""
        create_decision_cache_tables()
        with get_db_connection() as conn:
            if profile:
                conn.execute('DELETE FROM decision_cache WHERE profile = ?', (profile,))
            else:
                conn.execute('DELETE FROM decision_cache')

    @classmethod
    def get_cache_size(cls, profile: str) -> int:
        """Get the number of cached decisions for a profile."""
        create_decision_cache_tables()
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM decision_cache WHERE profile = ?', (profile,))
            row = cursor.fetchone()
            return row[0] if row else 0
