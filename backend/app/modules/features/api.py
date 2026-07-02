from fastapi import APIRouter, BackgroundTasks, Query, HTTPException, status
from loguru import logger

from app.modules.features.schema import FeatureStatusResponse, FeatureTopResponse, FeatureProfile
from app.modules.features.service import FeatureService
from app.modules.features.cache_service import FeatureCacheService
from app.modules.features.exceptions import (
    FeatureCacheNotBuiltError,
    FeatureActiveJobNotFoundError,
    FeatureServiceIntegrationError
)

# Router instance
router = APIRouter(prefix="/features", tags=["Feature Intelligence"])

# Global flag to track background cache build progress
_is_building_features = False

def _bg_rebuild_features_cache(force: bool, batch_size: int):
    """Background worker task to trigger candidates feature profile calculations."""
    global _is_building_features
    logger.info("Background thread started to compute candidate feature scorecards (force={force}, batch_size={batch_size}).",
                force=force, batch_size=batch_size)
    try:
        FeatureService.build_feature_profiles_cache(force_rebuild=force, batch_size=batch_size)
        logger.info("Background thread successfully completed candidate features cache computation.")
    except Exception as e:
        logger.exception("Error occurred during background features cache build: {err}", err=str(e))
    finally:
        _is_building_features = False

@router.post(
    "/build",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate candidate feature profiles cache"
)
async def build_features_cache(
    background_tasks: BackgroundTasks,
    force: bool = Query(default=False, description="Force rebuild feature scorecard profiles from scratch"),
    batch_size: int = Query(default=1000, ge=1, le=5000, description="Batch size for batch pipeline processing")
):
    """
    Triggers batch evaluations across all six feature dimensions for all candidates.
    Runs asynchronously in a background task to prevent API gateway timeouts.
    Check status using GET /api/v1/features/status.
    """
    global _is_building_features
    if _is_building_features:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Features cache build process is already active in the background."
        )
        
    _is_building_features = True
    background_tasks.add_task(_bg_rebuild_features_cache, force, batch_size)
    
    return {
        "status": "accepted",
        "message": "Candidate feature scorecards generation task started in the background."
    }

@router.get(
    "/status",
    response_model=FeatureStatusResponse,
    summary="Get cache statistics and build state"
)
async def get_cache_status():
    """
    Returns file size, modifications timestamps, record counts, and background build state.
    """
    try:
        status_data = FeatureCacheService.get_cache_status()
        
        # Override is_built flag if background task is currently active
        global _is_building_features
        if _is_building_features:
            status_data["is_built"] = False
            
        # Add processed speed throughput metrics
        status_data["candidates_processed_per_second"] = FeatureService.candidates_processed_per_second
        
        return status_data
    except Exception as e:
        logger.exception("Error retrieving features cache status: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch cache status: {str(e)}"
        )

@router.get(
    "/top",
    response_model=FeatureTopResponse,
    summary="Get highest feature scores by category"
)
async def get_top_candidates_by_category(
    limit: int = Query(default=5, ge=1, le=50, description="Number of top scorers to return per category")
):
    """
    Extracts candidate lists with top scores in Skills, Experience, Education, and Behavior categories.
    """
    try:
        results = FeatureService.get_top_candidates(limit=limit)
        return results
    except FeatureCacheNotBuiltError as fcnbe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(fcnbe)
        )
    except FeatureActiveJobNotFoundError as fajne:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fajne)
        )
    except FeatureServiceIntegrationError as fsie:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(fsie)
        )
    except Exception as e:
        logger.exception("Error querying top candidates by category: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top candidates: {str(e)}"
        )

@router.get(
    "/{candidate_id}",
    response_model=FeatureProfile,
    summary="Get candidate feature profile"
)
async def get_candidate_profile(candidate_id: str):
    """
    Returns the complete structured features profile scorecard for a candidate.
    """
    try:
        profile = FeatureService.get_candidate_profile(candidate_id)
        return profile
    except FeatureCacheNotBuiltError as fcnbe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(fcnbe)
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature profile scorecard for candidate {candidate_id} not found."
        )
    except Exception as e:
        logger.exception("Error retrieving candidate feature scorecard: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch candidate scorecard: {str(e)}"
        )

@router.delete(
    "/cache",
    summary="Delete features cache"
)
async def clear_cache():
    """
    Clears profile cache files from disk and cleans up in-memory caches.
    """
    try:
        FeatureCacheService.clear_cache()
        FeatureService.clear_memory_cache()
        return {
            "status": "success",
            "message": "Features disk cache and RAM memory cleared."
        }
    except Exception as e:
        logger.exception("Error clearing features cache: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clean features cache: {str(e)}"
        )
