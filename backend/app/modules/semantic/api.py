from fastapi import APIRouter, BackgroundTasks, Query, HTTPException, status
from loguru import logger
from typing import Dict, Any
import torch

from app.modules.jobs.service import JobService
from app.modules.semantic.schema import SemanticStatusResponse, SemanticTopResponse
from app.modules.semantic.service import SemanticService, get_current_memory_usage_mb
from app.modules.semantic.cache_service import CacheService
from app.modules.semantic.embedding_service import EmbeddingService
from app.modules.semantic.exceptions import (
    CacheNotBuiltError,
    ActiveJobNotFoundError,
    ServiceIntegrationError
)

# Router instance
router = APIRouter(prefix="/semantic", tags=["Semantic Intelligence"])

# Global flag tracking background build status
_is_building_cache = False

def _bg_rebuild_cache(force: bool, batch_size: int):
    """Background worker task to trigger vector encoding and persist cache files."""
    global _is_building_cache
    logger.info("Background thread started to rebuild vector cache (force={force}, batch_size={batch_size}).",
                force=force, batch_size=batch_size)
    try:
        SemanticService.build_candidate_embeddings_cache(force_rebuild=force, batch_size=batch_size)
        logger.info("Background thread successfully built and cached candidate vectors.")
    except Exception as e:
        logger.exception("Error occurred in background vector cache build: {err}", err=str(e))
    finally:
        _is_building_cache = False

@router.post(
    "/build",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate candidate embeddings cache"
)
async def build_candidate_cache(
    background_tasks: BackgroundTasks,
    force: bool = Query(default=False, description="Force rebuild embedding cache from scratch"),
    batch_size: int = Query(default=512, ge=1, le=2048, description="Batch size for SentenceTransformer encoding")
):
    """
    Triggers batch vector encoding for all valid candidate profiles.
    Runs asynchronously in a background task to prevent API gateway timeouts.
    Check status using GET /api/v1/semantic/status.
    """
    global _is_building_cache
    if _is_building_cache:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate embedding cache generation is already running in the background."
        )
        
    _is_building_cache = True
    background_tasks.add_task(_bg_rebuild_cache, force, batch_size)
    
    return {
        "status": "accepted",
        "message": "Candidate embeddings cache build task started in the background."
    }

@router.post(
    "/job",
    summary="Generate embedding for the active Job Description"
)
async def embed_active_job():
    """
    Fetches the active job description from Recruiter Layer and generates/caches its vector embedding in memory.
    """
    try:
        job_id, _, job_title = SemanticService.get_job_embedding()
        return {
            "status": "success",
            "message": f"Successfully generated and cached embedding for active job '{job_title}' ({job_id})."
        }
    except ActiveJobNotFoundError as ajne:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ajne)
        )
    except ServiceIntegrationError as sie:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(sie)
        )
    except Exception as e:
        logger.exception("Unexpected error embedding active job: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate active job embedding: {str(e)}"
        )

@router.get(
    "/top",
    response_model=SemanticTopResponse,
    summary="Retrieve ranked Top-K semantic matches"
)
async def get_top_candidates(
    limit: int = Query(default=100, description="Number of top matches to return. Allowed: 10, 25, 50, 100, 500")
):
    """
    Compares the active Job Description vector against the cached candidate vector matrix,
    calculating dot products (cosine similarity) and returning candidates ranked by relevance.
    """
    # 1. Enforce strict limit choices
    allowed_limits = {10, 25, 50, 100, 500}
    if limit not in allowed_limits:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid limit parameter. Choose one of: {sorted(list(allowed_limits))}"
        )
        
    try:
        results = SemanticService.get_top_candidates(limit=limit)
        
        # Populate performance telemetry
        results["model_load_time_ms"] = EmbeddingService.model_load_time_ms
        results["similarity_time_ms"] = SemanticService.last_similarity_time_ms
        results["memory_usage_mb"] = get_current_memory_usage_mb()
        
        return results
    except CacheNotBuiltError as cnbe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(cnbe)
        )
    except ActiveJobNotFoundError as ajne:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ajne)
        )
    except ServiceIntegrationError as sie:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(sie)
        )
    except Exception as e:
        logger.exception("Error matching candidates: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic matching process failed: {str(e)}"
        )

@router.get(
    "/status",
    response_model=SemanticStatusResponse,
    summary="Get cache statistics and build state"
)
async def get_cache_status():
    """
    Returns file system size, modification timestamps, vector counts, and background build state.
    """
    try:
        status_data = CacheService.get_cache_status()
        
        # Adjust is_built if currently building background task
        global _is_building_cache
        if _is_building_cache:
            status_data["is_built"] = False
            
        # Add latency telemetry
        status_data["model_load_time_ms"] = EmbeddingService.model_load_time_ms
        status_data["last_embedding_time_ms"] = SemanticService.last_embedding_time_ms
        status_data["memory_usage_mb"] = get_current_memory_usage_mb()
        
        return status_data
    except Exception as e:
        logger.exception("Error retrieving cache status: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch cache status: {str(e)}"
        )

@router.delete(
    "/cache",
    summary="Clear embedding cache files and RAM"
)
async def clear_cache():
    """
    Clears vector files from disk storage and cleans up in-memory cache matrices.
    """
    try:
        CacheService.clear_cache()
        SemanticService.clear_memory_cache()
        return {
            "status": "success",
            "message": "Disk files and in-memory caches cleared."
        }
    except Exception as e:
        logger.exception("Error clearing cache: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clean semantic cache: {str(e)}"
        )

@router.get(
    "/debug",
    summary="Get detailed semantic diagnostic information"
)
async def get_semantic_debug():
    """
    Returns diagnostic details: active job, Top 5 matches with raw scores, dimensions,
    model metadata, memory usage, and execution metrics.
    """
    # 1. Fetch cache status
    status_data = CacheService.get_cache_status()
    status_data["model_load_time_ms"] = EmbeddingService.model_load_time_ms
    status_data["last_embedding_time_ms"] = SemanticService.last_embedding_time_ms
    status_data["memory_usage_mb"] = get_current_memory_usage_mb()
    
    # 2. Model & Embedding Dimensions Info
    model_info = {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "dimensions": 384,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }
    
    # 3. Retrieve Active Job Info
    active_job = None
    try:
        active_job = JobService.get_active_job()
    except Exception:
        pass
        
    # 4. If cache is built and active job exists, query top 5 candidates
    top_candidates = []
    similarity_scores = []
    elapsed_ms = 0.0
    
    if status_data["is_built"] and active_job:
        try:
            # Query Top 10 matches (allowed limit)
            results = SemanticService.get_top_candidates(limit=10)
            # Take top 5
            top_candidates = results["matches"][:5]
            similarity_scores = [c["score"] for c in top_candidates]
            elapsed_ms = results["elapsed_ms"]
        except Exception as e:
            logger.warning("Debug endpoint failed to match candidates: {err}", err=str(e))
            
    # 5. Build Performance Metrics dict
    performance_metrics = {
        "model_load_time_ms": EmbeddingService.model_load_time_ms,
        "last_embedding_time_ms": SemanticService.last_embedding_time_ms,
        "last_similarity_time_ms": SemanticService.last_similarity_time_ms,
        "peak_memory_usage_mb": get_current_memory_usage_mb()
    }
    
    return {
        "current_job": {
            "id": active_job["id"] if active_job else None,
            "title": active_job["title"] if active_job else None,
            "required_skills": active_job["required_skills"] if active_job else []
        } if active_job else None,
        "top_5_candidates": [
            {
                "candidate_id": c["candidate_id"],
                "name": c["name"],
                "title": c["title"],
                "score": c["score"]
            }
            for c in top_candidates
        ],
        "similarity_scores": similarity_scores,
        "execution_time_ms": elapsed_ms,
        "embedding_dimensions": 384,
        "cache_status": status_data,
        "model_info": model_info,
        "performance_metrics": performance_metrics
    }
