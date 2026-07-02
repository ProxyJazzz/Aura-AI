import os
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

from app.modules.candidates.service import CandidateService
from app.modules.jobs.service import JobService
from app.modules.semantic.utils import format_candidate_text, format_job_text
from app.modules.semantic.embedding_service import EmbeddingService
from app.modules.semantic.cache_service import CacheService
from app.modules.semantic.similarity_service import SimilarityService
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
    
    # In-memory singletons for fast retrieval without disk reads
    _cached_matrix: Optional[np.ndarray] = None
    _cached_ids: Optional[List[str]] = None
    
    # In-memory cache for active job description embedding
    _active_job_id: Optional[str] = None
    _active_job_embedding: Optional[np.ndarray] = None
    
    # Execution metrics tracking
    last_embedding_time_ms: float = 0.0
    last_similarity_time_ms: float = 0.0

    @classmethod
    def load_cache_into_memory(cls, force: bool = False):
        """Load candidate embeddings from disk cache into RAM if not already loaded."""
        if force or cls._cached_matrix is None or cls._cached_ids is None:
            with Benchmark.time_operation("Load Embedding Cache to Memory"):
                matrix, ids = CacheService.load_cache()
                cls._cached_matrix = matrix
                cls._cached_ids = ids
                logger.info("Loaded vector matrix of shape {shape} into RAM.", shape=matrix.shape)

    @classmethod
    def clear_memory_cache(cls):
        """Discard in-memory singletons and resets metrics."""
        cls._cached_matrix = None
        cls._cached_ids = None
        cls._active_job_id = None
        cls._active_job_embedding = None
        cls.last_embedding_time_ms = 0.0
        cls.last_similarity_time_ms = 0.0
        logger.info("In-memory semantic cache and metrics cleared.")

    @classmethod
    def build_candidate_embeddings_cache(cls, force_rebuild: bool = False, batch_size: int = 512) -> Dict[str, Any]:
        """
        Retrieves valid candidate profiles through CandidateService, generates vector
        embeddings incrementally (only for new candidates), and saves them to the disk cache.
        """
        logger.info("Starting candidate embedding cache build (force_rebuild={force}, batch_size={batch})...", 
                    force=force_rebuild, batch=batch_size)
        
        # 1. Fetch valid candidates from CandidateService
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
                existing_matrix, existing_ids = CacheService.load_cache()
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
            # If force_rebuild is True OR candidate is not in cache, we process it
            if force_rebuild or cid not in existing_ids_set:
                candidates_to_embed.append(cand)
                
        logger.info("Total valid candidates: {total}. Candidates needing encoding: {needed}.", 
                    total=len(candidates), needed=len(candidates_to_embed))
                    
        # 4. If nothing is new, return existing status
        if not candidates_to_embed:
            logger.info("All candidate profiles are already cached. Skipping embedding generation.")
            cls.load_cache_into_memory()
            return CacheService.get_cache_status()
            
        # 5. Format texts for the new candidates
        texts = [format_candidate_text(cand) for cand in candidates_to_embed]
        new_ids = [cand["candidate_id"] for cand in candidates_to_embed]
        
        # 6. Generate embeddings for the new candidates
        start_time = time.perf_counter()
        with Benchmark.time_operation(f"Batch Encoding {len(new_ids)} Candidates"):
            new_embeddings = EmbeddingService.generate_embeddings(texts, batch_size=batch_size)
        cls.last_embedding_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        # 7. Merge new vectors with existing vectors
        if has_existing_cache and existing_matrix is not None:
            logger.info("Merging new vectors with existing cache matrix...")
            combined_matrix = np.concatenate([existing_matrix, new_embeddings], axis=0)
            combined_ids = existing_ids + new_ids
        else:
            combined_matrix = new_embeddings
            combined_ids = new_ids
            
        # 8. Write combined cache to disk
        CacheService.save_cache(combined_matrix, combined_ids)
        
        # 9. Reload RAM singletons
        cls.load_cache_into_memory(force=True)
        
        return CacheService.get_cache_status()

    @classmethod
    def get_job_embedding(cls) -> Tuple[str, np.ndarray, str]:
        """
        Retrieves the active job description via JobService, generates its embedding,
        and caches it in memory.
        """
        # Retrieve active job from JobService
        try:
            active_job = JobService.get_active_job()
        except Exception as e:
            logger.error("Failed to query active job from JobService: {err}", err=str(e))
            raise ServiceIntegrationError(f"JobService query failed: {str(e)}")
            
        if not active_job:
            raise ActiveJobNotFoundError("No active job description found. Please upload one first.")
            
        job_id = active_job["id"]
        job_title = active_job["title"]
        
        # Reuse cached embedding if matching
        if cls._active_job_id == job_id and cls._active_job_embedding is not None:
            logger.debug("Reusing cached in-memory job embedding for job ID: {id}", id=job_id)
            return job_id, cls._active_job_embedding, job_title
            
        # Otherwise, format text representation and encode
        logger.info("Active job ID changed or cache empty. Generating embedding for job: {title}...", title=job_title)
        job_text = format_job_text(active_job)
        
        start_time = time.perf_counter()
        with Benchmark.time_operation("Encode Active Job Description"):
            embeddings = EmbeddingService.generate_embeddings([job_text])
            job_embedding = embeddings[0]
        cls.last_embedding_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Cache in memory
        cls._active_job_id = job_id
        cls._active_job_embedding = job_embedding
        
        return job_id, job_embedding, job_title

    @classmethod
    def get_top_candidates(cls, limit: int = 100) -> Dict[str, Any]:
        """
        Compares the active job description vector against cached candidate vectors
        and returns the Top-K matching candidates sorted by cosine similarity score.
        """
        # Ensure candidate embeddings cache is loaded in memory
        try:
            cls.load_cache_into_memory()
        except (FileNotFoundError, ValueError):
            raise CacheNotBuiltError("Candidate embedding cache is not built. Please POST to /semantic/build first.")
            
        if cls._cached_matrix is None or cls._cached_ids is None:
            raise CacheNotBuiltError("Candidate embeddings cache is empty.")
            
        # Get active job embedding
        job_id, job_emb, job_title = cls.get_job_embedding()
        
        # Compute similarities & rank results
        start_time = time.perf_counter()
        with Benchmark.time_operation("Retrieve and Rank Top Matches") as timer:
            # 1. Cosine similarity via dot product
            scores = SimilarityService.compute_scores(cls._cached_matrix, job_emb)
            # 2. Top-K sorting
            ranked = SimilarityService.rank_candidates(scores, cls._cached_ids, limit)
        cls.last_similarity_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        elapsed_ms = timer["elapsed_ms"]
        
        # Gather details for Top-K candidates using CandidateService
        top_ids = [r[0] for r in ranked]
        scores_map = {r[0]: r[1] for r in ranked}
        
        if not top_ids:
            return {
                "job_id": job_id,
                "job_title": job_title,
                "matches": [],
                "limit": limit,
                "elapsed_ms": elapsed_ms
            }
            
        # 3. Batch query candidate profiles through CandidateService
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
            
        # Reconstruct ranked list preserving original similarity order
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
