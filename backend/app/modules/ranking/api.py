from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.modules.ranking.service import RankingService
from app.modules.ranking.configuration import RankingRequest, RankingEntry

router = APIRouter(tags=["Ranking"])

@router.post("/ranking/build", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def build_ranking(request: RankingRequest):
    """Trigger asynchronous ranking cache rebuild for the given weight profile."""
    try:
        await RankingService.build_cache_async(request.profile)
        return {"detail": f"Ranking cache rebuild started for profile '{request.profile}'."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/ranking/top", response_model=List[RankingEntry])
async def get_top(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    profile: Optional[str] = Query(None)
):
    """Return a page of top‑K ranked candidates."""
    try:
        return await RankingService.get_top(limit=limit, offset=offset, profile=profile)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/ranking/{candidate_id}", response_model=RankingEntry)
async def get_candidate(candidate_id: str, profile: Optional[str] = Query(None)):
    """Retrieve ranking entry for a specific candidate."""
    try:
        return await RankingService.get_candidate(candidate_id, profile=profile)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/ranking/status", response_model=dict)
async def get_status(profile: Optional[str] = Query(None)):
    """Return cache status (last build timestamp, size, hit count)."""
    try:
        return await RankingService.cache_status(profile)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/ranking/cache", response_model=dict)
async def clear_cache(profile: Optional[str] = Query(None)):
    """Clear cached rankings for the given profile (or all)."""
    try:
        await RankingService.clear_cache(profile)
        return {"detail": "Cache cleared."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
