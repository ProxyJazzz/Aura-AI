from fastapi import APIRouter, UploadFile, File, HTTPException, status
from loguru import logger

from app.modules.jobs.schema import JobResponse
from app.modules.jobs.service import JobService
from app.modules.jobs.repository import JobRepository

# Define APIRouters
router = APIRouter(tags=["Jobs"])

@router.post(
    "/jobs/upload",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new Job Description (.docx)"
)
async def upload_job_description(file: UploadFile = File(...)):
    """
    Accepts a Job Description in DOCX format, extracts and normalizes the text,
    runs rule-based extraction to populate structured fields, and saves it as
    the active job description in SQLite.
    """
    filename = file.filename or ""
    if not filename.lower().endswith(".docx"):
        logger.warning("Rejected job upload with invalid extension: {filename}", filename=filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a Microsoft Word (.docx) document."
        )
        
    try:
        content = await file.read()
        logger.info("Processing job upload: {filename} ({bytes} bytes)", filename=filename, bytes=len(content))
        
        # 1. Convert DOCX bytes to raw text
        raw_text = JobService.docx_to_text(content)
        
        # 2. Heuristic extraction of Job fields
        parsed_job = JobService.extract_job_details(raw_text)
        
        # 3. Save to database (will set as active and deactivate older ones)
        saved_record = JobRepository.save_job(raw_text, parsed_job)
        
        return saved_record
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception("Unexpected error uploading job description: {err}", err=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal database error occurred while parsing and saving the job description."
        )

@router.get(
    "/jobs/current",
    response_model=JobResponse,
    summary="Get the current active Job Description"
)
async def get_current_job():
    """
    Retrieves the currently active job description profile.
    """
    try:
        active_job = JobRepository.get_active_job()
        if not active_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active job description found. Please upload a .docx file to initialize."
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
    "/jobs/summary",
    summary="Get summary metrics of the current active Job Description"
)
async def get_job_summary():
    """
    Retrieves statistical metrics for the currently active job description,
    including required and preferred skill counts.
    """
    try:
        active_job = JobRepository.get_active_job()
        if not active_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active job description found. Please upload a .docx file to initialize."
            )
            
        return {
            "id": active_job["id"],
            "title": active_job["title"],
            "required_skills_count": len(active_job["required_skills"]),
            "preferred_skills_count": len(active_job["preferred_skills"]),
            "min_experience_years": active_job["min_experience"],
            "seniority": active_job["seniority"],
            "employment_type": active_job["employment_type"],
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
