from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.modules.decision.service import DecisionService
from app.modules.decision.schema import DecisionRequest, DecisionProfileSchema

router = APIRouter(tags=["Decision"])

@router.post("/decision/build", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def build_decision(request: DecisionRequest):
    """Trigger asynchronous decision cache rebuild for the given weight profile."""
    try:
        await DecisionService.build_cache_async(request.profile)
        return {"detail": f"Decision cache rebuild started for profile '{request.profile}'."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/decision/top", response_model=List[DecisionProfileSchema])
async def get_top(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    profile: Optional[str] = Query(None)
):
    """Return a page of top-K ranked candidates with decision profiles."""
    try:
        return await DecisionService.get_top(limit=limit, offset=offset, profile=profile)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/decision/{candidate_id}", response_model=DecisionProfileSchema)
async def get_candidate(candidate_id: str, profile: Optional[str] = Query(None)):
    """Retrieve decision profile for a specific candidate."""
    try:
        return await DecisionService.get_candidate(candidate_id, profile=profile)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/decision/status", response_model=dict)
async def get_status(profile: Optional[str] = Query(None)):
    """Return cache status (last build timestamp, size, hit count)."""
    try:
        return await DecisionService.cache_status(profile)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/decision/cache", response_model=dict)
async def clear_cache(profile: Optional[str] = Query(None)):
    """Clear cached decisions for the given profile (or all)."""
    try:
        await DecisionService.clear_cache(profile)
        return {"detail": "Decision cache cleared."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
