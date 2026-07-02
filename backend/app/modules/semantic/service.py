import os
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

from app.modules.candidates.service import CandidateService
from app.modules.jobs.service import JobService
from app.modules.semantic.utils import format_candidate_text, format_job_text
from app.modules.semantic.embedding_manager import EmbeddingManager
from app.modules.semantic.candidate_encoder import CandidateEncoder
from app.modules.semantic.job_encoder import JobEncoder
from app.modules.semantic.similarity_engine import SimilarityEngine
from app.modules.semantic.embedding_cache import EmbeddingCache
from app.modules.semantic.semantic_match import SemanticMatch
from app.modules.semantic.repository import SemanticRepository
from app.modules.semantic.benchmark import Benchmark
from app.modules.semantic.exceptions import (
    CacheNotBuiltError,
    ActiveJobNotFoundError,
    ServiceIntegrationError
)


def get_current_memory_usage_mb() -> float:
    """Helper to check current RAM footprint of the Python process in MB."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return round(process.memory_info().rss / (1024 * 1024), 2)
    except ImportError:
        return 0.0


class SemanticService:
    """Orchestrates candidate vector generation, caching, and similarity lookup workflows."""

    last_embedding_time_ms: float = 0.0
    last_similarity_time_ms: float = 0.0

    @classmethod
    def load_cache_into_memory(cls, force: bool = False) -> None:
        """Load candidate embeddings from disk cache into RAM if not already loaded."""
        with Benchmark.time_operation("Load Embedding Cache to Memory"):
            EmbeddingCache.load_candidate_cache(force)

    @classmethod
    def clear_memory_cache(cls) -> None:
        """Discard in-memory cached vectors and reset performance metrics."""
        EmbeddingCache.clear()
        cls.last_embedding_time_ms = 0.0
        cls.last_similarity_time_ms = 0.0
        logger.info("In-memory cache and performance telemetry metrics reset.")

    @classmethod
    def build_candidate_embeddings_cache(
        cls, force_rebuild: bool = False, batch_size: int = 512
    ) -> Dict[str, Any]:
        """Generate candidate embeddings incrementally and update embedding cache."""
        logger.info(
            "Starting candidate embedding cache build (force_rebuild={force}, batch_size={batch})...",
            force=force_rebuild,
            batch=batch_size
        )

        # 1. Fetch valid candidates
        try:
            with Benchmark.time_operation("Retrieve Candidates via CandidateService"):
                candidates = CandidateService.get_valid_candidates()
        except Exception as e:
            logger.error("Failed to fetch candidates from CandidateService: {err}", err=str(e))
            raise ServiceIntegrationError(f"CandidateService query failed: {str(e)}")

        if not candidates:
            raise ServiceIntegrationError("CandidateService returned an empty list of valid candidates.")

        # 2. Check if cache already exists for incremental loads
        existing_matrix: Optional[np.ndarray] = None
        existing_ids: List[str] = []
        has_existing_cache = False

        if not force_rebuild:
            try:
                existing_matrix, existing_ids = EmbeddingCache.load_candidate_cache()
                has_existing_cache = True
                logger.info("Found existing cache with {count} candidate vectors.", count=len(existing_ids))
            except (FileNotFoundError, ValueError):
                logger.info("No valid pre-existing cache found. Building from scratch.")

        # 3. Filter candidates to process
        candidates_to_embed = []
        existing_ids_set = set(existing_ids)

        for cand in candidates:
            cid = cand.get("candidate_id")
            if not cid:
                continue
            if force_rebuild or cid not in existing_ids_set:
                candidates_to_embed.append(cand)

        logger.info(
            "Total valid candidates: {total}. Candidates needing encoding: {needed}.",
            total=len(candidates),
            needed=len(candidates_to_embed)
        )

        # 4. If nothing is new, return status
        if not candidates_to_embed:
            logger.info("All candidate profiles are already cached. Skipping embedding generation.")
            cls.load_cache_into_memory()
            return EmbeddingCache.get_status()

        # 5. Generate embeddings in batch
        start_time = time.perf_counter()
        with Benchmark.time_operation(f"Batch Encoding {len(candidates_to_embed)} Candidates"):
            new_embeddings = CandidateEncoder.encode_candidates(candidates_to_embed, batch_size=batch_size)
        cls.last_embedding_time_ms = (time.perf_counter() - start_time) * 1000.0

        new_ids = [c["candidate_id"] for c in candidates_to_embed]

        # 6. Merge with existing cache
        if has_existing_cache and existing_matrix is not None:
            logger.info("Merging new vectors with existing cache matrix...")
            combined_matrix = np.concatenate([existing_matrix, new_embeddings], axis=0)
            combined_ids = existing_ids + new_ids
        else:
            combined_matrix = new_embeddings
            combined_ids = new_ids

        # 7. Write combined cache to disk
        EmbeddingCache.save_candidate_cache(combined_matrix, combined_ids)

        # 8. Reload RAM singletons
        cls.load_cache_into_memory(force=True)

        return EmbeddingCache.get_status()

    @classmethod
    def get_job_embedding(cls) -> Tuple[str, np.ndarray, str]:
        """Retrieves active job description details and generates/caches its vector embedding."""
        try:
            active_job = JobService.get_active_job()
        except Exception as e:
            logger.error("Failed to query active job from JobService: {err}", err=str(e))
            raise ServiceIntegrationError(f"JobService query failed: {str(e)}")

        if not active_job:
            raise ActiveJobNotFoundError("No active job description found. Please upload one first.")

        job_id = active_job["id"]
        job_title = active_job["title"]

        # Fetch from cache first
        cached = EmbeddingCache.get_job_embedding(job_id)
        if cached is not None:
            return job_id, cached, job_title

        logger.info("Generating embedding for job: {title}...", title=job_title)
        
        start_time = time.perf_counter()
        with Benchmark.time_operation("Encode Active Job Description"):
            job_embedding = JobEncoder.encode_job(active_job)
        cls.last_embedding_time_ms = (time.perf_counter() - start_time) * 1000.0

        # Save to cache
        EmbeddingCache.save_job_embedding(job_id, job_embedding)

        return job_id, job_embedding, job_title

    @classmethod
    def get_top_candidates(cls, limit: int = 100) -> Dict[str, Any]:
        """Compares active job vector against cached candidate vectors and returns Top-K matches."""
        # Load candidate cache
        try:
            cls.load_cache_into_memory()
        except (FileNotFoundError, ValueError):
            raise CacheNotBuiltError(
                "Candidate embedding cache is not built. Please POST to /semantic/build first."
            )

        matrix, ids = EmbeddingCache.load_candidate_cache()
        if matrix is None or ids is None or len(ids) == 0:
            raise CacheNotBuiltError("Candidate embeddings cache is empty.")

        # Get active job embedding
        job_id, job_emb, job_title = cls.get_job_embedding()

        # Compute similarities & rank results
        start_time = time.perf_counter()
        with Benchmark.time_operation("Retrieve and Rank Top Matches") as timer:
            matches_dicts = SimilarityEngine.compute_similarity(job_emb, matrix, ids)
            
            # Sort top K
            ranked_matches = sorted(
                [SemanticMatch.from_dict(m) for m in matches_dicts],
                key=lambda x: x.score,
                reverse=True
            )[:limit]
            
        cls.last_similarity_time_ms = (time.perf_counter() - start_time) * 1000.0
        elapsed_ms = timer["elapsed_ms"]

        # Persist semantic matches in database
        EmbeddingCache.save_semantic_matches(job_id, [m.to_dict() for m in ranked_matches])

        top_ids = [m.candidate_id for m in ranked_matches]
        scores_map = {m.candidate_id: m.score for m in ranked_matches}

        if not top_ids:
            return {
                "job_id": job_id,
                "job_title": job_title,
                "matches": [],
                "limit": limit,
                "elapsed_ms": elapsed_ms
            }

        # Query candidate profiles details
        try:
            with Benchmark.time_operation("Retrieve Candidate Details via CandidateService"):
                rows = CandidateService.get_candidates_by_ids(top_ids)
        except Exception as e:
            logger.error("Failed to retrieve candidate profiles from CandidateService: {err}", err=str(e))
            raise ServiceIntegrationError(f"CandidateService lookup failed: {str(e)}")

        details_map = {}
        for row in rows:
            details_map[row["candidate_id"]] = {
                "name": row["anonymized_name"],
                "title": row["current_title"],
                "experience": row["years_of_experience"],
                "location": row["location"],
                "skills": [s.strip() for s in row["skills_list"].split(",") if s.strip()] if row["skills_list"] else []
            }

        matches = []
        for cid in top_ids:
            if cid in details_map:
                details = details_map[cid]
                matches.append({
                    "candidate_id": cid,
                    "name": details["name"],
                    "title": details["title"],
                    "score": round(scores_map[cid], 2),
                    "experience": details["experience"],
                    "location": details["location"],
                    "skills": details["skills"]
                })

        return {
            "job_id": job_id,
            "job_title": job_title,
            "matches": matches,
            "limit": limit,
            "elapsed_ms": round(elapsed_ms, 2)
        }
