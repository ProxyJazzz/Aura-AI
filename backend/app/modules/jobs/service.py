import re
from typing import Dict, Any, List, Optional
from loguru import logger

from app.modules.jobs.schema import JobModel, Seniority, EmploymentType
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.parser import JobParserFactory
from app.modules.jobs.validator import JobValidator
from app.modules.jobs.hiring_profile import HiringProfileGenerator
from app.modules.jobs.cache import JobCache
from app.modules.jobs.exceptions import FileValidationError
from app.modules.jobs.utils import clean_text
from app.modules.jobs.metadata_extractor import JobMetadataExtractor
from app.modules.jobs.requirement_classifier import JobRequirementClassifier, ALL_TECH_SKILLS, ALL_SOFT_SKILLS


class JobService:
    """Service handling DOCX/TXT ingestion, text parsing, section categorization, and metadata extraction."""

    @staticmethod
    def docx_to_text(file_bytes: bytes) -> str:
        """Extract raw text from a DOCX file byte stream."""
        parser = JobParserFactory.get_parser("job.docx")
        return parser.parse(file_bytes)

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean up spacing and line endings."""
        return clean_text(text)

    @classmethod
    def extract_job_details(cls, raw_text: str) -> JobModel:
        """Legacy helper extracting basic JobModel details for backwards compatibility."""
        cleaned = clean_text(raw_text)
        metadata = JobMetadataExtractor.extract_metadata(cleaned)
        
        # Build sections map for requirement classification
        from app.modules.jobs.section_detector import JobSectionDetector
        sections = JobSectionDetector.detect_sections(cleaned)
        reqs = JobRequirementClassifier.classify_requirements(sections)

        return JobModel(
            title=metadata["title"],
            required_skills=reqs["required_skills"],
            preferred_skills=reqs["preferred_skills"],
            min_experience=metadata["min_experience"],
            seniority=metadata["seniority"],
            industry=metadata["industry"],
            employment_type=metadata["employment_type"],
            soft_skills=reqs["soft_skills"]
        )

    @classmethod
    def process_upload(cls, filename: str, content: bytes) -> Dict[str, Any]:
        """Validate, parse, extract, compile and save a job description upload."""
        # 1. Validate size, type, corruption, and checksum
        upload_info = JobValidator.validate_upload(filename, content)
        
        # 2. Check for duplicate checksum in history
        history = JobRepository.get_history()
        for h in history:
            if h["checksum"] == upload_info["checksum"]:
                raise FileValidationError(f"This job description file has already been uploaded (ID: {h['id']}).")

        # 3. Parse raw text
        parser = JobParserFactory.get_parser(filename)
        raw_text = parser.parse(content)
        cleaned = clean_text(raw_text)

        # 4. Generate structured hiring profile
        hiring_profile = HiringProfileGenerator.generate(cleaned, upload_info)

        # 5. Extract legacy JobModel fields for database schema compliance
        job_model = cls.extract_job_details(cleaned)

        # 6. Save to repository
        saved_job = JobRepository.save_job_profile(
            raw_text=cleaned,
            parsed_job=job_model,
            hiring_profile=hiring_profile,
            upload_metadata=upload_info
        )

        # 7. Update in-memory cache
        JobCache.set_active_profile(hiring_profile)

        return saved_job

    @classmethod
    def get_active_profile(cls) -> Optional[Dict[str, Any]]:
        """Retrieve the currently active Hiring Profile object."""
        cached = JobCache.get_active_profile()
        if cached:
            return cached

        active_job = JobRepository.get_active_job()
        if active_job and active_job.get("hiring_profile"):
            JobCache.set_active_profile(active_job["hiring_profile"])
            return active_job["hiring_profile"]
        return None

    @classmethod
    def get_active_job(cls) -> Optional[Dict[str, Any]]:
        """Retrieve the active job database record."""
        return JobRepository.get_active_job()

    @classmethod
    def delete_active_job(cls) -> bool:
        """Deactivate or remove the currently active job description."""
        deleted = JobRepository.delete_current()
        if deleted:
            JobCache.clear()
        return deleted

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Fetch current status indicators of recruiter intelligence."""
        active = JobRepository.get_active_job()
        return {
            "has_active_job": active is not None,
            "active_job_id": active["id"] if active else None,
            "active_job_title": active["title"] if active else None
        }
