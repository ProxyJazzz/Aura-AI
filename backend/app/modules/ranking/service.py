import yaml
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

from app.modules.features.service import FeatureService
from app.modules.ranking.configuration import RankingEntry


class RankingService:
    """Orchestrates candidate scoring aggregation, weight loading, and cache management."""

    # In-memory store for calculated rankings
    _cached_rankings: Dict[str, List[RankingEntry]] = {}
    _last_build_time: Dict[str, str] = {}
    _build_count: Dict[str, int] = {}

    @classmethod
    def _load_weights(cls, profile_name: str) -> Dict[str, float]:
        """Load weights for the given profile from app/config/profiles.yaml."""
        backend_root = Path(__file__).resolve().parent.parent.parent.parent
        yaml_path = backend_root / "app" / "config" / "profiles.yaml"
        
        if not yaml_path.exists():
            logger.warning("profiles.yaml not found at {path}. Using default generic weights.", path=yaml_path)
            return {
                "semantic": 25.0,
                "skills": 20.0,
                "experience": 15.0,
                "education": 10.0,
                "behavior": 10.0,
                "certification": 10.0,
                "language": 10.0,
            }

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        profiles = data.get("profiles", {})
        if profile_name not in profiles:
            logger.warning("Weight profile '{name}' not found. Falling back to generic.", name=profile_name)
            profile_name = "generic"
            
        weights = profiles.get(profile_name, {})
        # Fill missing with default 0
        all_keys = ["semantic", "skills", "experience", "education", "behavior", "certification", "language"]
        return {k: float(weights.get(k, 0.0)) for k in all_keys}

    @classmethod
    def _compute_ranking(cls, profile_name: str) -> List[RankingEntry]:
        """Compute the weighted overall scores and sort candidates."""
        FeatureService.load_cache_into_memory()
        profiles = FeatureService._cached_profiles or {}
        if not profiles:
            logger.warning("Feature cache is empty; ranking cannot be generated.")
            return []

        weights = cls._load_weights(profile_name)
        rankings: List[RankingEntry] = []

        for cid, pf in profiles.items():
            # Compute weighted sum
            semantic = float(pf.get("semantic_score", 0.0))
            skills = float(pf.get("skill_score", 0.0))
            experience = float(pf.get("experience_score", 0.0))
            education = float(pf.get("education_score", 0.0))
            certification = float(pf.get("certification_score", 0.0))
            language = float(pf.get("language_score", 0.0))
            behavior = float(pf.get("behavior_score", 0.0))

            overall_score = (
                semantic * weights.get("semantic", 0.0) +
                skills * weights.get("skills", 0.0) +
                experience * weights.get("experience", 0.0) +
                education * weights.get("education", 0.0) +
                certification * weights.get("certification", 0.0) +
                language * weights.get("language", 0.0) +
                behavior * weights.get("behavior", 0.0)
            ) / 100.0

            overall_score = min(100.0, max(0.0, round(overall_score, 2)))

            # Mock Decision Intelligence fields
            if overall_score >= 85:
                decision = "STRONG_YES"
                confidence = round(0.85 + (overall_score - 85) * 0.01, 2)
                recommendation = "Highly qualified candidate. Recommend immediate interview."
            elif overall_score >= 70:
                decision = "YES"
                confidence = round(0.70 + (overall_score - 70) * 0.01, 2)
                recommendation = "Qualified candidate. Proceed to screening."
            elif overall_score >= 50:
                decision = "MAYBE"
                confidence = round(0.60 + (overall_score - 50) * 0.005, 2)
                recommendation = "Potential match. Keep in talent pool."
            else:
                decision = "NO"
                confidence = round(0.80 - overall_score * 0.005, 2)
                recommendation = "Low fit alignment. Reconsider."

            entry = RankingEntry(
                candidate_id=cid,
                overall_score=overall_score,
                semantic_score=semantic,
                skill_score=skills,
                experience_score=experience,
                education_score=education,
                certification_score=certification,
                language_score=language,
                behavior_score=behavior,
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
            pf["reason_codes"] = ["SKILL_MATCH"] if skills >= 70 else []

        # Deterministic sorting
        # 1. overall_score (desc)
        # 2. semantic_score (desc)
        # 3. skill_score (desc)
        # 4. experience_score (desc)
        # 5. candidate_id (asc)
        rankings.sort(key=lambda x: (
            -x.overall_score,
            -x.semantic_score,
            -x.skill_score,
            -x.experience_score,
            x.candidate_id
        ))

        return rankings

    @classmethod
    async def build_cache_async(cls, profile: str) -> None:
        """Trigger asynchronous ranking cache rebuild."""
        profile = profile or "generic"
        logger.info("Rebuilding ranking cache for profile '{profile}'", profile=profile)
        cls._cached_rankings[profile] = cls._compute_ranking(profile)
        cls._last_build_time[profile] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        cls._build_count[profile] = cls._build_count.get(profile, 0) + 1

    @classmethod
    async def get_top(cls, limit: int = 10, offset: int = 0, profile: Optional[str] = None) -> List[RankingEntry]:
        """Return a page of top-K ranked candidates."""
        profile = profile or "generic"
        if profile not in cls._cached_rankings:
            # Synchronously trigger if not built
            cls._cached_rankings[profile] = cls._compute_ranking(profile)
            cls._last_build_time[profile] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            cls._build_count[profile] = cls._build_count.get(profile, 0) + 1
            
        dataset = cls._cached_rankings[profile]
        return dataset[offset : offset + limit]

    @classmethod
    async def get_candidate(cls, candidate_id: str, profile: Optional[str] = None) -> RankingEntry:
        """Retrieve ranking entry for a specific candidate."""
        profile = profile or "generic"
        if profile not in cls._cached_rankings:
            cls._cached_rankings[profile] = cls._compute_ranking(profile)
            cls._last_build_time[profile] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            cls._build_count[profile] = cls._build_count.get(profile, 0) + 1

        for r in cls._cached_rankings[profile]:
            if r.candidate_id == candidate_id:
                return r
        raise KeyError(f"Candidate '{candidate_id}' not found in ranking list.")

    @classmethod
    async def cache_status(cls, profile: Optional[str] = None) -> dict:
        """Return cache status."""
        profile = profile or "generic"
        is_built = profile in cls._cached_rankings
        return {
            "is_built": is_built,
            "last_build": cls._last_build_time.get(profile),
            "size": len(cls._cached_rankings.get(profile, [])),
            "hits": cls._build_count.get(profile, 0)
        }

    @classmethod
    async def clear_cache(cls, profile: Optional[str] = None) -> None:
        """Clear cached rankings."""
        if profile:
            cls._cached_rankings.pop(profile, None)
            cls._last_build_time.pop(profile, None)
        else:
            cls._cached_rankings.clear()
            cls._last_build_time.clear()
        logger.info("Ranking cache cleared.")
