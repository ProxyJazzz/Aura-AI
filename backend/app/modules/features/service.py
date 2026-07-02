import time
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

from app.modules.candidates.service import CandidateService
from app.modules.jobs.service import JobService
from app.modules.semantic.service import SemanticService
from app.modules.features.cache import FeatureCache
from app.modules.features.feature_profile import FeatureProfileGenerator
from app.modules.features.benchmark import FeatureBenchmark
from app.modules.features.exceptions import (
    FeatureCacheNotBuiltError,
    FeatureActiveJobNotFoundError,
    FeatureServiceIntegrationError
)

# Import all independent scoring engines
from app.modules.features.skill_engine import SkillEngine
from app.modules.features.experience_engine import ExperienceEngine
from app.modules.features.education_engine import EducationEngine
from app.modules.features.certification_engine import CertificationEngine
from app.modules.features.language_engine import LanguageEngine
from app.modules.features.behavior_engine import BehaviorEngine


class FeatureService:
    """Orchestrates candidate scoring dimensions, caching, and categorical rankings."""

    _cached_profiles: Optional[Dict[str, Dict[str, Any]]] = None
    candidates_processed_per_second: float = 0.0

    @classmethod
    def load_cache_into_memory(cls, force: bool = False) -> None:
        """Loads feature profiles from database or disk cache into RAM."""
        if force or cls._cached_profiles is None:
            try:
                cls._cached_profiles = FeatureCache.load_profiles(force)
                logger.info("Loaded {count} feature profiles from cache into memory.", count=len(cls._cached_profiles))
            except Exception as e:
                raise FeatureCacheNotBuiltError(f"Features profile cache load failed: {str(e)}")

    @classmethod
    def clear_memory_cache(cls) -> None:
        """Discards memory, file, and database cached scorecards."""
        FeatureCache.clear()
        cls._cached_profiles = None
        cls.candidates_processed_per_second = 0.0
        logger.info("Features memory cache and databases truncated.")

    @classmethod
    def build_feature_profiles_cache(
        cls, force_rebuild: bool = False, batch_size: int = 1000
    ) -> Dict[str, Any]:
        """Runs candidate feature evaluations and updates cache incrementally."""
        logger.info("Building Feature Intelligence profiles cache (force={force})...", force=force_rebuild)
        start_time = time.perf_counter()

        # 1. Fetch Job
        try:
            active_job = JobService.get_active_job()
        except Exception as e:
            raise FeatureServiceIntegrationError(f"JobService retrieval failed: {str(e)}")

        if not active_job:
            raise FeatureActiveJobNotFoundError("No active job description found. Features cannot be calculated.")

        # 2. Fetch Candidates
        try:
            candidates = CandidateService.get_valid_candidates()
        except Exception as e:
            raise FeatureServiceIntegrationError(f"CandidateService retrieval failed: {str(e)}")

        if not candidates:
            raise FeatureServiceIntegrationError("CandidateService returned 0 valid candidates.")

        # 3. Fetch Semantic Scores
        try:
            semantic_results = SemanticService.get_top_candidates(limit=100000)
            semantic_map = {m["candidate_id"]: m["score"] for m in semantic_results["matches"]}
        except Exception as e:
            logger.error("Failed to retrieve semantic scores: {err}", err=str(e))
            raise FeatureServiceIntegrationError(
                f"Failed to retrieve semantic similarity scores. Ensure Semantic Cache is built: {str(e)}"
            )

        # 4. Handle Incremental Cache Rebuild
        existing_profiles: Dict[str, Dict[str, Any]] = {}
        if not force_rebuild:
            try:
                existing_profiles = FeatureCache.load_profiles()
                logger.info("Found existing cache containing {count} feature profiles.", count=len(existing_profiles))
            except Exception:
                logger.info("No valid pre-existing cache found. Building from scratch.")

        # 5. Filter candidates requiring scoring
        candidates_to_score = []
        for cand in candidates:
            cid = cand.get("candidate_id")
            if not cid:
                continue
            if force_rebuild or cid not in existing_profiles:
                candidates_to_score.append(cand)

        logger.info(
            "Total candidates: {total}. Candidates to evaluate: {needed}.",
            total=len(candidates),
            needed=len(candidates_to_score)
        )

        # If no candidates need evaluation, return status
        if not candidates_to_score:
            logger.info("All feature profiles are already cached. Skipping computation.")
            cls.load_cache_into_memory(force=True)
            return FeatureCache.get_status()

        # 6. Initialize scoring engines
        skill_engine = SkillEngine()
        exp_engine = ExperienceEngine()
        edu_engine = EducationEngine()
        cert_engine = CertificationEngine()
        lang_engine = LanguageEngine()
        behavior_engine = BehaviorEngine()

        scored_profiles = {}
        total_to_process = len(candidates_to_score)

        # Evaluate candidates
        for cand in candidates_to_score:
            cid = cand["candidate_id"]

            skill_score, skill_meta = skill_engine.calculate(cand, active_job)
            exp_score, exp_meta = exp_engine.calculate(cand, active_job)
            edu_score, edu_meta = edu_engine.calculate(cand, active_job)
            cert_score, cert_meta = cert_engine.calculate(cand, active_job)
            lang_score, lang_meta = lang_engine.calculate(cand, active_job)
            behavior_score, behavior_meta = behavior_engine.calculate(cand, active_job)

            semantic_score = float(semantic_map.get(cid, 0.0))

            # Generate structured profile
            profile = FeatureProfileGenerator.construct_profile(
                candidate_id=cid,
                semantic_score=semantic_score,
                skill_score=skill_score,
                experience_score=exp_score,
                education_score=edu_score,
                certification_score=cert_score,
                language_score=lang_score,
                behavior_score=behavior_score,
                metadata={
                    "skill": skill_meta,
                    "experience": exp_meta,
                    "education": edu_meta,
                    "certification": cert_meta,
                    "language": lang_meta,
                    "behavior": behavior_meta
                }
            )
            scored_profiles[cid] = profile

        # Merge and save
        merged = {**existing_profiles, **scored_profiles}
        FeatureCache.save_profiles(merged)

        # Reload cache into RAM
        cls.load_cache_into_memory(force=True)

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        cls.candidates_processed_per_second = FeatureBenchmark.calculate_throughput(
            total_to_process, duration_ms
        )

        logger.info(
            "Successfully finished scoring. Throughput: {tps} candidates/sec.",
            tps=cls.candidates_processed_per_second
        )

        status = FeatureCache.get_status()
        status["candidates_processed_per_second"] = cls.candidates_processed_per_second
        return status

    @classmethod
    def get_candidate_profile(cls, candidate_id: str) -> Dict[str, Any]:
        """Fetch a single candidate's scored feature profile from cache."""
        cls.load_cache_into_memory()

        if cls._cached_profiles is None or candidate_id not in cls._cached_profiles:
            raise KeyError(f"Feature profile scorecard for candidate {candidate_id} not found.")

        return cls._cached_profiles[candidate_id]

    @classmethod
    def get_top_candidates(cls, limit: int = 5) -> Dict[str, Any]:
        """Sorts profiles across main categories and returns Top-K candidates for each."""
        cls.load_cache_into_memory()
        if not cls._cached_profiles:
            raise FeatureCacheNotBuiltError("Features cache is empty.")

        active_job = JobService.get_active_job()
        if not active_job:
            raise FeatureActiveJobNotFoundError("No active job description set.")

        job_id = active_job["id"]
        job_title = active_job["title"]

        profiles = list(cls._cached_profiles.values())

        # Sort top candidates per category
        top_skills = sorted(profiles, key=lambda x: x["skill_score"], reverse=True)[:limit]
        top_exp = sorted(profiles, key=lambda x: x["experience_score"], reverse=True)[:limit]
        top_edu = sorted(profiles, key=lambda x: x["education_score"], reverse=True)[:limit]
        top_behavior = sorted(profiles, key=lambda x: x["behavior_score"], reverse=True)[:limit]

        # Gather all top candidate IDs
        all_top_ids = list(set([c["candidate_id"] for c in top_skills + top_exp + top_edu + top_behavior]))

        # Batch query names and titles
        try:
            candidate_details = CandidateService.get_candidates_by_ids(all_top_ids)
            details_map = {
                c["candidate_id"]: {
                    "name": c["anonymized_name"],
                    "title": c["current_title"]
                }
                for c in candidate_details
            }
        except Exception as e:
            logger.error("Failed to query candidate details: {err}", err=str(e))
            details_map = {}

        def map_details(c_list: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
            results = []
            for c in c_list:
                cid = c["candidate_id"]
                details = details_map.get(cid, {"name": "Anonymized", "title": "Developer"})
                results.append({
                    "candidate_id": cid,
                    "name": details["name"],
                    "title": details["title"],
                    "score": c[key]
                })
            return results

        return {
            "job_id": job_id,
            "job_title": job_title,
            "skills": map_details(top_skills, "skill_score"),
            "experience": map_details(top_exp, "experience_score"),
            "education": map_details(top_edu, "education_score"),
            "behavior": map_details(top_behavior, "behavior_score")
        }
