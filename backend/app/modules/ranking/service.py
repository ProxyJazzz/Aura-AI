import time
from typing import List, Optional, Dict
from loguru import logger

from app.modules.features.service import FeatureService
from app.modules.ranking.configuration import RankingEntry
from app.modules.ranking.weight_engine import WeightEngine
from app.modules.ranking.aggregation_engine import AggregationEngine
from app.modules.ranking.confidence_engine import ConfidenceEngine
from app.modules.ranking.ranking_engine import RankingEngine
from app.modules.ranking.ranking_cache import RankingCache
from app.modules.ranking.exceptions import FeatureCacheEmptyError

class RankingService:
    """Orchestrates candidate scoring aggregation, weight loading, and cache management."""

    @classmethod
    def _compute_ranking(cls, profile_name: str) -> List[RankingEntry]:
        """Compute the weighted overall scores and sort candidates."""
        FeatureService.load_cache_into_memory()
        profiles = FeatureService._cached_profiles or {}
        if not profiles:
            logger.warning("Feature cache is empty; ranking cannot be generated.")
            return []

        weights = WeightEngine.load_weights(profile_name)
        rankings: List[RankingEntry] = []

        for cid, pf in profiles.items():
            # Compute weighted sum
            overall_score = AggregationEngine.compute_overall_score(pf, weights)

            # Decision Intelligence fields
            decision, confidence, recommendation = ConfidenceEngine.evaluate(overall_score)

            entry = RankingEntry(
                candidate_id=cid,
                overall_score=overall_score,
                semantic_score=float(pf.get("semantic_score", 0.0)),
                skill_score=float(pf.get("skill_score", 0.0)),
                experience_score=float(pf.get("experience_score", 0.0)),
                education_score=float(pf.get("education_score", 0.0)),
                certification_score=float(pf.get("certification_score", 0.0)),
                language_score=float(pf.get("language_score", 0.0)),
                behavior_score=float(pf.get("behavior_score", 0.0)),
                decision=decision,
                confidence=confidence,
                recommendation=recommendation
            )
            rankings.append(entry)

            # Update the FeatureService cached profiles dict directly so the export module can access it
            pf["overall_score"] = overall_score
            pf["decision"] = decision
            pf["confidence"] = confidence
            pf["recommendation"] = recommendation
            pf["reason_codes"] = ["SKILL_MATCH"] if entry.skill_score >= 70 else []

        # Deterministic sorting
        return RankingEngine.rank(rankings)

    @classmethod
    async def build_cache_async(cls, profile: str) -> None:
        """Trigger asynchronous ranking cache rebuild."""
        profile = profile or "generic"
        logger.info(f"Rebuilding ranking cache for profile '{profile}'")
        rankings = cls._compute_ranking(profile)
        RankingCache.save_rankings(profile, rankings)

    @classmethod
    async def get_top(cls, limit: int = 10, offset: int = 0, profile: Optional[str] = None) -> List[RankingEntry]:
        """Return a page of top-K ranked candidates."""
        profile = profile or "generic"
        if not RankingCache.is_cached(profile):
            # Synchronously trigger if not built
            rankings = cls._compute_ranking(profile)
            RankingCache.save_rankings(profile, rankings)
            
        return RankingCache.get_top(profile, limit, offset)

    @classmethod
    async def get_candidate(cls, candidate_id: str, profile: Optional[str] = None) -> RankingEntry:
        """Retrieve ranking entry for a specific candidate."""
        profile = profile or "generic"
        if not RankingCache.is_cached(profile):
            rankings = cls._compute_ranking(profile)
            RankingCache.save_rankings(profile, rankings)

        entry = RankingCache.get_candidate(candidate_id, profile)
        if entry:
            return entry
        raise KeyError(f"Candidate '{candidate_id}' not found in ranking list.")

    @classmethod
    async def cache_status(cls, profile: Optional[str] = None) -> dict:
        """Return cache status."""
        profile = profile or "generic"
        return RankingCache.get_status(profile)

    @classmethod
    async def clear_cache(cls, profile: Optional[str] = None) -> None:
        """Clear cached rankings."""
        RankingCache.clear(profile)
        logger.info("Ranking cache cleared.")
