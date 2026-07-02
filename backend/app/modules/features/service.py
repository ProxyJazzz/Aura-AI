import time
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

from app.modules.candidates.service import CandidateService
from app.modules.jobs.service import JobService
from app.modules.semantic.service import SemanticService
from app.modules.features.cache_service import FeatureCacheService
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
    
    # In-memory singleton cache to prevent disk lookups on query endpoints
    _cached_profiles: Optional[Dict[str, Dict[str, Any]]] = None
    
    # Throughput tracker
    candidates_processed_per_second: float = 0.0

    @classmethod
    def load_cache_into_memory(cls, force: bool = False):
        """Loads feature profiles from disk cache into RAM if not already loaded."""
        if force or cls._cached_profiles is None:
            try:
                cls._cached_profiles = FeatureCacheService.load_cache()
                logger.info("Loaded {count} feature profiles from disk cache into memory.", 
                            count=len(cls._cached_profiles))
            except FileNotFoundError:
                raise FeatureCacheNotBuiltError("Features profile cache does not exist.")

    @classmethod
    def clear_memory_cache(cls):
        """Discards RAM singletons."""
        cls._cached_profiles = None
        cls.candidates_processed_per_second = 0.0
        logger.info("Features memory cache cleared.")

    @classmethod
    def build_feature_profiles_cache(cls, force_rebuild: bool = False, batch_size: int = 1000) -> Dict[str, Any]:
        """
        Retrieves candidates and jobs, queries semantic scores, runs evaluations across all 
        six dimensions, and updates cache files incrementally.
        """
        logger.info("Building Feature intelligence profiles cache (force={force})...", force=force_rebuild)
        start_time = time.perf_counter()
        
        # 1. Fetch Job from Recruiter Layer
        try:
            active_job = JobService.get_active_job()
        except Exception as e:
            raise FeatureServiceIntegrationError(f"JobService retrieval failed: {str(e)}")
            
        if not active_job:
            raise FeatureActiveJobNotFoundError("No active job description found. Features cannot be calculated.")
            
        # 2. Fetch Candidates from Candidate Layer
        try:
            candidates = CandidateService.get_valid_candidates()
        except Exception as e:
            raise FeatureServiceIntegrationError(f"CandidateService retrieval failed: {str(e)}")
            
        if not candidates:
            raise FeatureServiceIntegrationError("CandidateService returned 0 valid candidates.")
            
        # 3. Read semantic scores (read-only from Semantic Service)
        # Note: SemanticService cache must be built first!
        try:
            semantic_results = SemanticService.get_top_candidates(limit=100000)
            semantic_map = {m["candidate_id"]: m["score"] for m in semantic_results["matches"]}
        except Exception as e:
            logger.error("Failed to retrieve semantic scores: {err}", err=str(e))
            raise FeatureServiceIntegrationError(
                f"Failed to retrieve semantic similarity scores. Ensure Semantic Cache is built: {str(e)}"
            )
            
        # 4. Handle incremental caching (check which profiles are already cached)
        existing_profiles: Dict[str, Dict[str, Any]] = {}
        if not force_rebuild:
            try:
                existing_profiles = FeatureCacheService.load_cache()
                logger.info("Found existing cache containing {count} feature profiles.", count=len(existing_profiles))
            except (FileNotFoundError, ValueError):
                logger.info("No valid pre-existing cache found. Building from scratch.")
                
        # 5. Filter candidates requiring scoring
        candidates_to_score = []
        for cand in candidates:
            cid = cand.get("candidate_id")
            if not cid:
                continue
            if force_rebuild or cid not in existing_profiles:
                candidates_to_score.append(cand)
                
        logger.info("Total candidates: {total}. Candidates to evaluate: {needed}.", 
                    total=len(candidates), needed=len(candidates_to_embed := candidates_to_score))
                    
        # If no candidates require recalculation, load cache and return status
        if not candidates_to_score:
            logger.info("All feature profiles are already cached. Skipping computation.")
            cls.load_cache_into_memory(force=True)
            return FeatureCacheService.get_cache_status()
            
        # 6. Initialize independent scoring engines
        skill_engine = SkillEngine()
        exp_engine = ExperienceEngine()
        edu_engine = EducationEngine()
        cert_engine = CertificationEngine()
        lang_engine = LanguageEngine()
        behavior_engine = BehaviorEngine()
        
        # 7. Evaluate candidates in batches
        scored_profiles = {}
        total_to_process = len(candidates_to_score)
        
        logger.info("Evaluating feature scorecards in batches of {batch}...", batch=batch_size)
        
        for i, cand in enumerate(candidates_to_score):
            cid = cand["candidate_id"]
            
            # Run evaluations
            skill_score, skill_meta = skill_engine.calculate(cand, active_job)
            exp_score, exp_meta = exp_engine.calculate(cand, active_job)
            edu_score, edu_meta = edu_engine.calculate(cand, active_job)
            cert_score, cert_meta = cert_engine.calculate(cand, active_job)
            lang_score, lang_meta = lang_engine.calculate(cand, active_job)
            behavior_score, behavior_meta = behavior_engine.calculate(cand, active_job)
            
            # Fetch semantic score
            semantic_score = float(semantic_map.get(cid, 0.0))
            
            # Construct feature vector
            feature_vector = [
                semantic_score,
                skill_score,
                exp_score,
                edu_score,
                cert_score,
                lang_score,
                behavior_score
            ]
            
            # Construct complete profile
            scored_profiles[cid] = {
                "candidate_id": cid,
                "semantic_score": round(semantic_score, 2),
                "skill_score": round(skill_score, 2),
                "experience_score": round(exp_score, 2),
                "education_score": round(edu_score, 2),
                "certification_score": round(cert_score, 2),
                "language_score": round(lang_score, 2),
                "behavior_score": round(behavior_score, 2),
                "feature_vector": [round(v, 2) for v in feature_vector],
                "metadata": {
                    "skill": skill_meta,
                    "experience": exp_meta,
                    "education": edu_meta,
                    "certification": cert_meta,
                    "language": lang_meta,
                    "behavior": behavior_meta
                }
            }
            
        # 8. Merge and Save to disk
        merged_profiles = {**existing_profiles, **scored_profiles}
        FeatureCacheService.save_cache(merged_profiles)
        
        # 9. Reload RAM singletons
        cls.load_cache_into_memory(force=True)
        
        # Calculate performance throughput
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        cls.candidates_processed_per_second = FeatureBenchmark.calculate_throughput(
            total_to_process, duration_ms
        )
        
        logger.info("Successfully finished scoring. Throughput: {tps} candidates/sec.", 
                    tps=cls.candidates_processed_per_second)
                    
        status = FeatureCacheService.get_cache_status()
        status["candidates_processed_per_second"] = cls.candidates_processed_per_second
        return status

    @classmethod
    def get_candidate_profile(cls, candidate_id: str) -> Dict[str, Any]:
        """Fetch a single candidate's scored feature profile from RAM cache."""
        cls.load_cache_into_memory()
        
        if cls._cached_profiles is None or candidate_id not in cls._cached_profiles:
            raise KeyError(f"Feature profile scorecard for candidate {candidate_id} not found.")
            
        return cls._cached_profiles[candidate_id]

    @classmethod
    def get_top_candidates(cls, limit: int = 5) -> Dict[str, Any]:
        """
        Sorts profiles across Skill, Experience, Education, and Behavior categories
        and returns the Top-K candidates for each category.
        """
        # Ensure cache is loaded
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
        all_top_ids = list(set(
            [c["candidate_id"] for c in top_skills + top_exp + top_edu + top_behavior]
        ))
        
        # Batch query name and current title from CandidateService
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
            
        # Helper to construct CategoryTopCandidate payload
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
