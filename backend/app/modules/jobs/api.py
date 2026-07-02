from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from loguru import logger

from app.modules.jobs.schema import JobResponse
from app.modules.jobs.service import JobService
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.exceptions import FileValidationError

# Define APIRouter with jobs prefix
router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/upload",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new Job Description (.docx or .txt)"
)
async def upload_job_description(file: UploadFile = File(...)):
    """
    Accepts a Job Description in DOCX or TXT format, validates, extracts,
    normalizes, and categorizes into a structured Hiring Profile, setting it as active.
    """
    filename = file.filename or ""
    try:
        content = await file.read()
        logger.info("Processing job upload: {filename} ({bytes} bytes)", filename=filename, bytes=len(content))
        saved_record = JobService.process_upload(filename, content)
        return saved_record
    except FileValidationError as fve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(fve)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception("Unexpected error uploading job description: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing and saving the job description: {str(e)}"
        )


@router.get(
    "/current",
    response_model=JobResponse,
    summary="Get the current active Job Description"
)
async def get_current_job():
    """Retrieves the currently active job description profile."""
    try:
        active_job = JobService.get_active_job()
        if not active_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active job description found. Please upload a file to initialize."
            )
        return active_job
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching active job description: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve active job from database."
        )


@router.get(
    "/profile",
    summary="Get the current active structured Hiring Profile"
)
async def get_active_hiring_profile():
    """Retrieves the current active structured Hiring Profile object."""
    try:
        profile = JobService.get_active_profile()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active hiring profile found."
            )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching active hiring profile: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve active hiring profile."
        )


@router.get(
    "/history",
    summary="Get upload history metadata"
)
async def get_job_history():
    """Retrieves metadata for all uploaded job descriptions."""
    try:
        return JobRepository.get_history()
    except Exception as e:
        logger.exception("Error fetching upload history: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve upload history."
        )


@router.delete(
    "/current",
    summary="Deactivate/Delete the current active Job Description"
)
async def delete_current_job():
    """Deactivates the currently active job description."""
    try:
        success = JobService.delete_active_job()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active job description found to delete."
            )
        return {"detail": "Active job description deactivated successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deactivating job description: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not deactivate active job description."
        )


@router.get(
    "/status",
    summary="Get status details of the active job description"
)
async def get_status():
    """Fetch status of job description settings."""
    try:
        return JobService.get_status()
    except Exception as e:
        logger.exception("Error getting status: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve status."
        )


@router.get(
    "/summary",
    summary="Get summary metrics of the current active Job Description"
)
async def get_job_summary():
    """Retrieves statistical metrics for the currently active job description."""
    try:
        active_job = JobService.get_active_job()
        if not active_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active job description found. Please upload a file to initialize."
            )
            
        # Support string/enum checking
        seniority = active_job["seniority"]
        if hasattr(seniority, "value"):
            seniority = seniority.value
            
        emp_type = active_job["employment_type"]
        if hasattr(emp_type, "value"):
            emp_type = emp_type.value

        return {
            "id": active_job["id"],
            "title": active_job["title"],
            "required_skills_count": len(active_job["required_skills"]),
            "preferred_skills_count": len(active_job["preferred_skills"]),
            "min_experience_years": active_job["min_experience"],
            "seniority": seniority,
            "employment_type": emp_type,
            "industry": active_job["industry"],
            "soft_skills_count": len(active_job["soft_skills"])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating job summary metrics: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve job summary metrics."
        )
