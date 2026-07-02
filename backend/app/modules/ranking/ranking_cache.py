from typing import List, Optional, Dict
import time
from loguru import logger

from app.modules.ranking.configuration import RankingEntry
from app.modules.ranking.repository import RankingRepository

class RankingCache:
    """Manages persistent SQLite cache for candidate rankings."""

    _last_build_time: Dict[str, str] = {}
    _build_count: Dict[str, int] = {}

    @classmethod
    def save_rankings(cls, profile: str, rankings: List[RankingEntry]):
        """Save a batch of candidate rankings to the database."""
        ranking_dicts = [r.dict() for r in rankings]
        RankingRepository.save_rankings(profile, ranking_dicts)
        
        cls._last_build_time[profile] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        cls._build_count[profile] = cls._build_count.get(profile, 0) + 1
        logger.info(f"Saved {len(rankings)} rankings to cache for profile '{profile}'")

    @classmethod
    def get_top(cls, profile: str, limit: int = 10, offset: int = 0) -> List[RankingEntry]:
        """Fetch top candidates from the cache for a given profile."""
        rows = RankingRepository.get_top_candidates(profile, limit, offset)
        return [RankingEntry(**r) for r in rows]

    @classmethod
    def get_candidate(cls, candidate_id: str, profile: str) -> Optional[RankingEntry]:
        """Fetch a specific candidate's ranking from the cache."""
        row = RankingRepository.get_candidate(candidate_id, profile)
        if row:
            return RankingEntry(**row)
        return None

    @classmethod
    def is_cached(cls, profile: str) -> bool:
        """Check if a profile has cached rankings."""
        return RankingRepository.get_cache_size(profile) > 0

    @classmethod
    def clear(cls, profile: Optional[str] = None):
        """Clear cache."""
        RankingRepository.clear_cache(profile)
        if profile:
            cls._last_build_time.pop(profile, None)
        else:
            cls._last_build_time.clear()

    @classmethod
    def get_status(cls, profile: str) -> dict:
        """Get cache status for a profile."""
        size = RankingRepository.get_cache_size(profile)
        return {
            "is_built": size > 0,
            "last_build": cls._last_build_time.get(profile),
            "size": size,
            "hits": cls._build_count.get(profile, 0)
        }
