import time
from typing import List, Optional, Dict
from loguru import logger

from app.modules.decision.schema import DecisionProfileSchema
from app.modules.decision.repository import DecisionRepository
from app.modules.decision.utils import parse_string_to_list

class DecisionCache:
    """Manages persistent SQLite cache for candidate decisions."""

    _last_build_time: Dict[str, str] = {}
    _build_count: Dict[str, int] = {}

    @classmethod
    def save_decisions(cls, profile: str, decisions: List[dict]):
        """Save a batch of candidate decisions to the database."""
        DecisionRepository.save_decisions(profile, decisions)
        cls._last_build_time[profile] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        cls._build_count[profile] = cls._build_count.get(profile, 0) + 1
        logger.info(f"Saved {len(decisions)} decisions to cache for profile '{profile}'")

    @classmethod
    def _map_to_schema(cls, row: dict) -> DecisionProfileSchema:
        return DecisionProfileSchema(
            candidate_id=row["candidate_id"],
            profile=row["profile"],
            rank=row["rank"],
            overall_score=row["overall_score"],
            recommendation=row["recommendation"],
            confidence=row["confidence"],
            risk_level=row["risk_level"],
            reason_codes=parse_string_to_list(row["reason_codes"]),
            strengths=parse_string_to_list(row["strengths"]),
            gaps=parse_string_to_list(row["gaps"]),
            next_action=row["next_action"]
        )

    @classmethod
    def get_top(cls, profile: str, limit: int = 10, offset: int = 0) -> List[DecisionProfileSchema]:
        """Fetch top candidates from the cache for a given profile."""
        rows = DecisionRepository.get_top_decisions(profile, limit, offset)
        return [cls._map_to_schema(r) for r in rows]

    @classmethod
    def get_candidate(cls, candidate_id: str, profile: str) -> Optional[DecisionProfileSchema]:
        """Fetch a specific candidate's decision from the cache."""
        row = DecisionRepository.get_candidate(candidate_id, profile)
        if row:
            return cls._map_to_schema(row)
        return None

    @classmethod
    def is_cached(cls, profile: str) -> bool:
        """Check if a profile has cached decisions."""
        return DecisionRepository.get_cache_size(profile) > 0

    @classmethod
    def clear(cls, profile: Optional[str] = None):
        """Clear cache."""
        DecisionRepository.clear_cache(profile)
        if profile:
            cls._last_build_time.pop(profile, None)
        else:
            cls._last_build_time.clear()

    @classmethod
    def get_status(cls, profile: str) -> dict:
        """Get cache status for a profile."""
        size = DecisionRepository.get_cache_size(profile)
        return {
            "is_built": size > 0,
            "last_build": cls._last_build_time.get(profile),
            "size": size,
            "hits": cls._build_count.get(profile, 0)
        }
