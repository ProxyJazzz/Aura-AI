from typing import List, Optional, Dict, Any
from loguru import logger
from app.shared.database.connection import get_db_connection
from app.modules.ranking.models import create_ranking_cache_tables

class RankingRepository:
    """Handles database operations for Ranking cache."""

    @classmethod
    def get_top_candidates(cls, profile: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Fetch top candidates from the cache for a given profile."""
        create_ranking_cache_tables()
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM ranking_cache 
                WHERE profile = ?
                ORDER BY overall_score DESC, semantic_score DESC, skill_score DESC, experience_score DESC, candidate_id ASC
                LIMIT ? OFFSET ?
            ''', (profile, limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def get_candidate(cls, candidate_id: str, profile: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific candidate's ranking from the cache."""
        create_ranking_cache_tables()
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM ranking_cache 
                WHERE candidate_id = ? AND profile = ?
            ''', (candidate_id, profile))
            row = cursor.fetchone()
            return dict(row) if row else None

    @classmethod
    def save_rankings(cls, profile: str, rankings: List[dict]):
        """Save a batch of candidate rankings to the cache, overwriting the old ones for this profile."""
        create_ranking_cache_tables()
        with get_db_connection() as conn:
            conn.execute('DELETE FROM ranking_cache WHERE profile = ?', (profile,))
            
            if not rankings:
                return
                
            columns = [
                "candidate_id", "profile", "overall_score", "semantic_score", 
                "skill_score", "experience_score", "education_score", "certification_score", 
                "language_score", "behavior_score", "decision", "confidence", "recommendation"
            ]
            
            placeholders = ", ".join(["?"] * len(columns))
            query = f"INSERT INTO ranking_cache ({', '.join(columns)}) VALUES ({placeholders})"
            
            data = []
            for r in rankings:
                data.append((
                    r["candidate_id"],
                    profile,
                    r["overall_score"],
                    r["semantic_score"],
                    r["skill_score"],
                    r["experience_score"],
                    r["education_score"],
                    r["certification_score"],
                    r["language_score"],
                    r["behavior_score"],
                    r.get("decision"),
                    r.get("confidence"),
                    r.get("recommendation")
                ))
                
            conn.executemany(query, data)

    @classmethod
    def clear_cache(cls, profile: Optional[str] = None):
        """Clear cache for a specific profile or all profiles."""
        create_ranking_cache_tables()
        with get_db_connection() as conn:
            if profile:
                conn.execute('DELETE FROM ranking_cache WHERE profile = ?', (profile,))
            else:
                conn.execute('DELETE FROM ranking_cache')

    @classmethod
    def get_cache_size(cls, profile: str) -> int:
        """Get the number of cached rankings for a profile."""
        create_ranking_cache_tables()
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM ranking_cache WHERE profile = ?', (profile,))
            return cursor.fetchone()[0]
