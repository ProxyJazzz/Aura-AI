import json
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from loguru import logger

from app.modules.candidates.schema import (
    CandidateListResponse,
    CandidateDetailResponse,
    DatasetSummaryResponse,
    CandidateModel
)
from app.modules.candidates.repository import CandidateRepository
from app.modules.candidates.service import CandidateService

# ── Router Definitions ───────────────────────────────────────────

candidates_router = APIRouter(prefix="/candidates", tags=["Candidates"])
dataset_router = APIRouter(prefix="/dataset", tags=["Dataset"])

# ── Candidate Endpoints ──────────────────────────────────────────

@candidates_router.get(
    "",
    response_model=CandidateListResponse,
    summary="Retrieve candidates",
    description="Gets a list of candidates from the dataset with support for filtering, sorting, and pagination."
)
async def get_candidates(
    skill: Optional[str] = Query(default=None, description="Filter candidates by a specific skill name"),
    min_experience: Optional[float] = Query(default=None, ge=0, le=50, description="Minimum years of experience"),
    max_experience: Optional[float] = Query(default=None, ge=0, le=50, description="Maximum years of experience"),
    open_to_work: Optional[bool] = Query(default=None, description="Filter candidates by open-to-work flag"),
    location: Optional[str] = Query(default=None, description="Filter by location (partial match)"),
    is_valid: Optional[bool] = Query(default=None, description="Filter by validation status"),
    is_honeypot: Optional[bool] = Query(default=None, description="Filter by honeypot status"),
    sort_by: str = Query(
        default="candidate_id",
        description="Field to sort by. Allowed fields: candidate_id, years_of_experience, profile_completeness_score, recruiter_response_rate, avg_response_time_hours, num_companies."
    ),
    sort_order: str = Query(default="asc", description="Sort order: 'asc' or 'desc'"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip")
) -> CandidateListResponse:
    """List candidates matching criteria."""
    try:
        candidates, total = CandidateRepository.get_candidates(
            skill=skill,
            min_experience=min_experience,
            max_experience=max_experience,
            open_to_work=open_to_work,
            location=location,
            is_valid=is_valid,
            is_honeypot=is_honeypot,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        
        return CandidateListResponse(
            items=candidates,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error("Error retrieving candidates: {e}", e=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database error: {str(e)}"
        )

@candidates_router.get(
    "/{candidate_id}",
    response_model=CandidateDetailResponse,
    summary="Retrieve candidate details",
    description="Gets detailed information about a single candidate, including raw data and extracted features."
)
async def get_candidate_by_id(candidate_id: str) -> CandidateDetailResponse:
    """Retrieve detailed candidate by ID."""
    try:
        candidate = CandidateRepository.get_candidate_by_id(candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with ID {candidate_id} not found"
            )
            
        is_valid = bool(candidate["is_valid"])
        is_honeypot = bool(candidate["is_honeypot"])
        val_error = candidate["validation_error"]
        raw_json_str = candidate["raw_json"]
        
        # Reconstruct Pydantic model for data if valid
        data_model = None
        if is_valid:
            try:
                data_model = CandidateModel(**json.loads(raw_json_str))
            except Exception as e:
                logger.warning("Failed to deserialize candidate raw_json: {e}", e=str(e))
                
        # Extract features sub-dict
        features = {
            "anonymized_name": candidate["anonymized_name"],
            "location": candidate["location"],
            "country": candidate["country"],
            "years_of_experience": candidate["years_of_experience"],
            "current_title": candidate["current_title"],
            "current_company": candidate["current_company"],
            "profile_completeness_score": candidate["profile_completeness_score"],
            "recruiter_response_rate": candidate["recruiter_response_rate"],
            "avg_response_time_hours": candidate["avg_response_time_hours"],
            "open_to_work_flag": bool(candidate["open_to_work_flag"]),
            "skills_list": candidate["skills_list"],
            "primary_skills_count": candidate["primary_skills_count"],
            "has_ai_ml_skills": bool(candidate["has_ai_ml_skills"]),
            "has_only_consulting_experience": bool(candidate["has_only_consulting_experience"]),
            "has_worked_in_consulting": bool(candidate["has_worked_in_consulting"]),
            "num_companies": candidate["num_companies"],
            "avg_tenure_months": candidate["avg_tenure_months"],
            "highest_education_tier": candidate["highest_education_tier"],
            "has_masters_or_phd": bool(candidate["has_masters_or_phd"]),
            "num_certifications": candidate["num_certifications"],
            "num_languages": candidate["num_languages"],
            "last_active_date": candidate["last_active_date"]
        }
        
        return CandidateDetailResponse(
            candidate_id=candidate_id,
            is_valid=is_valid,
            is_honeypot=is_honeypot,
            validation_error=val_error,
            data=data_model,
            raw_json=raw_json_str,
            features=features
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving candidate details: {e}", e=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database error: {str(e)}"
        )

# ── Dataset Endpoints ────────────────────────────────────────────

@dataset_router.get(
    "/summary",
    response_model=DatasetSummaryResponse,
    summary="Get dataset summary and statistics",
    description="Returns global analytics, distributions, and summary statistics computed over the dataset."
)
async def get_dataset_summary() -> DatasetSummaryResponse:
    """Get dataset summary stats."""
    try:
        stats = CandidateRepository.get_statistics()
        if not stats:
            # Stats not precalculated yet, try computing on-the-fly (fallback)
            logger.warning("Dataset statistics not precalculated in cache. Calculating on-the-fly...")
            stats = CandidateService.calculate_global_statistics()
            CandidateRepository.save_statistics(stats)
            
        return DatasetSummaryResponse(**stats)
    except Exception as e:
        logger.error("Error retrieving dataset summary: {e}", e=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error compiling statistics: {str(e)}"
        )
