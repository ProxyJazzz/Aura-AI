import time
from typing import List, Optional
from loguru import logger

from app.modules.ranking.service import RankingService
from app.modules.decision.decision_profile import DecisionProfile
from app.modules.decision.decision_engine import DecisionEngine
from app.modules.decision.cache import DecisionCache
from app.modules.decision.schema import DecisionProfileSchema
from app.modules.decision.exceptions import RankingCacheEmptyError

class DecisionService:
    """Orchestrates candidate decision generation and cache management."""

    @classmethod
    async def _compute_decisions(cls, profile_name: str) -> List[dict]:
        """Fetch rankings, run decision engine, and return list of dictionaries."""
        try:
            # We fetch all candidates (up to a large limit) to build decisions
            rankings = await RankingService.get_top(limit=10000, profile=profile_name)
        except KeyError:
            raise RankingCacheEmptyError(f"Ranking cache for profile '{profile_name}' is empty. Build ranking first.")

        if not rankings:
            logger.warning(f"No candidates found in ranking cache for profile '{profile_name}'.")
            return []

        decisions = []
        for i, r in enumerate(rankings):
            # Create internal decision profile
            dp = DecisionProfile(
                candidate_id=r.candidate_id,
                profile=profile_name,
                rank=i + 1,
                overall_score=r.overall_score,
                semantic_score=r.semantic_score,
                skill_score=r.skill_score,
                experience_score=r.experience_score,
                education_score=r.education_score,
                certification_score=r.certification_score,
                language_score=r.language_score,
                behavior_score=r.behavior_score
            )
            
            # Pipe through engine
            dp = DecisionEngine.evaluate_profile(dp)
            decisions.append(dp.to_dict())

        return decisions

    @classmethod
    async def build_cache_async(cls, profile: str) -> None:
        """Trigger asynchronous decision cache rebuild."""
        profile = profile or "generic"
        logger.info(f"Rebuilding decision cache for profile '{profile}'")
        decisions = await cls._compute_decisions(profile)
        DecisionCache.save_decisions(profile, decisions)

    @classmethod
    async def get_top(cls, limit: int = 10, offset: int = 0, profile: Optional[str] = None) -> List[DecisionProfileSchema]:
        """Return a page of top-K decision profiles."""
        profile = profile or "generic"
        if not DecisionCache.is_cached(profile):
            # Synchronously trigger if not built
            decisions = await cls._compute_decisions(profile)
            DecisionCache.save_decisions(profile, decisions)
            
        return DecisionCache.get_top(profile, limit, offset)

    @classmethod
    async def get_candidate(cls, candidate_id: str, profile: Optional[str] = None) -> DecisionProfileSchema:
        """Retrieve decision entry for a specific candidate."""
        profile = profile or "generic"
        if not DecisionCache.is_cached(profile):
            decisions = await cls._compute_decisions(profile)
            DecisionCache.save_decisions(profile, decisions)

        entry = DecisionCache.get_candidate(candidate_id, profile)
        if entry:
            return entry
        raise KeyError(f"Candidate '{candidate_id}' not found in decision list.")

    @classmethod
    async def cache_status(cls, profile: Optional[str] = None) -> dict:
        """Return cache status."""
        profile = profile or "generic"
        return DecisionCache.get_status(profile)

    @classmethod
    async def clear_cache(cls, profile: Optional[str] = None) -> None:
        """Clear cached decisions."""
        DecisionCache.clear(profile)
        logger.info("Decision cache cleared.")
