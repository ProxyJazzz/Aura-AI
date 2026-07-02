from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional

from app.modules.intelligence.service import IntelligenceService
from app.modules.intelligence.schema import (
    DashboardIntelligence,
    CandidateComparisonResponse,
    MarketIntelligence,
    PipelineHealth,
    RecruiterInsights,
    ReadinessIntelligence
)
from app.modules.intelligence.exceptions import CandidateNotFoundError

router = APIRouter(tags=["Intelligence"])

@router.get("/intelligence/dashboard", response_model=DashboardIntelligence)
async def get_dashboard(profile: str = Query("generic")):
    """Get high-level dashboard metrics for the talent pool."""
    try:
        return await IntelligenceService.get_dashboard(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/insights", response_model=RecruiterInsights)
async def get_insights(profile: str = Query("generic")):
    """Get deterministic recruiter insights and action items."""
    try:
        return await IntelligenceService.get_insights(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/market", response_model=MarketIntelligence)
async def get_market():
    """Get market intelligence derived from the entire candidate pool."""
    try:
        return await IntelligenceService.get_market()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/pipeline", response_model=PipelineHealth)
async def get_pipeline(profile: str = Query("generic")):
    """Get candidate ingestion pipeline health and AI confidence."""
    try:
        return await IntelligenceService.get_pipeline_health(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/compare/{candidate1}/{candidate2}", response_model=CandidateComparisonResponse)
async def compare_candidates(candidate1: str, candidate2: str, profile: str = Query("generic")):
    """Compare two candidates deterministically based on their decision profiles."""
    try:
        return await IntelligenceService.compare(candidate1, candidate2, profile)
    except CandidateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/readiness", response_model=ReadinessIntelligence)
async def get_readiness(profile: str = Query("generic")):
    """Get overall hiring readiness and bottleneck analysis."""
    try:
        return await IntelligenceService.get_readiness(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
