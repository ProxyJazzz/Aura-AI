import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from loguru import logger

from app.shared.database import get_db_connection
from app.modules.jobs.schema import JobModel
from app.modules.jobs.models import (
    CREATE_JOBS_TABLE,
    CREATE_JOBS_INDEX,
    ALTER_JOBS_PROFILE,
    ALTER_JOBS_METADATA
)


class JobRepository:
    """Repository handling SQLite operations for job profiles."""

    @staticmethod
    def create_tables():
        """Create the jobs table and associated indexes if they do not exist."""
        with get_db_connection() as conn:
            conn.execute(CREATE_JOBS_TABLE)
            conn.execute(CREATE_JOBS_INDEX)
            
            # Check for column existence to run schema migrations
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(jobs);")
            columns = [row["name"] for row in cursor.fetchall()]
            
            if "hiring_profile" not in columns:
                try:
                    conn.execute(ALTER_JOBS_PROFILE)
                    logger.info("Migrated jobs table: Added hiring_profile column.")
                except Exception as e:
                    logger.warning("Failed to add hiring_profile column: {e}", e=str(e))
                    
            if "upload_metadata" not in columns:
                try:
                    conn.execute(ALTER_JOBS_METADATA)
                    logger.info("Migrated jobs table: Added upload_metadata column.")
                except Exception as e:
                    logger.warning("Failed to add upload_metadata column: {e}", e=str(e))

            logger.info("Jobs table initialized successfully.")

    @staticmethod
    def save_job(raw_text: str, parsed_job: JobModel) -> Dict[str, Any]:
        """Legacy save_job method for compatibility with older modules."""
        # Call the new save_job_profile with empty/default dicts
        return JobRepository.save_job_profile(
            raw_text=raw_text,
            parsed_job=parsed_job,
            hiring_profile={},
            upload_metadata={"filename": "legacy.docx", "file_size": 0, "content_type": "unknown", "checksum": ""}
        )

    @staticmethod
    def save_job_profile(
        raw_text: str,
        parsed_job: JobModel,
        hiring_profile: Dict[str, Any],
        upload_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deactivate previous jobs, save the new job profile as active, and return saved details."""
        JobRepository.create_tables()
        
        job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        req_skills_json = json.dumps(parsed_job.required_skills)
        pref_skills_json = json.dumps(parsed_job.preferred_skills)
        soft_skills_json = json.dumps(parsed_job.soft_skills)
        hiring_profile_json = json.dumps(hiring_profile)
        upload_metadata_json = json.dumps(upload_metadata)
        
        with get_db_connection() as conn:
            # Deactivate all existing jobs
            conn.execute("UPDATE jobs SET is_active = 0;")
            
            # Insert the new active job
            conn.execute(
                """
                INSERT INTO jobs (
                    id, title, raw_text, required_skills, preferred_skills,
                    min_experience, seniority, industry, employment_type,
                    soft_skills, created_at, is_active, hiring_profile, upload_metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?);
                """,
                (
                    job_id,
                    parsed_job.title,
                    raw_text,
                    req_skills_json,
                    pref_skills_json,
                    parsed_job.min_experience,
                    parsed_job.seniority.value,
                    parsed_job.industry,
                    parsed_job.employment_type.value,
                    soft_skills_json,
                    created_at,
                    hiring_profile_json,
                    upload_metadata_json
                )
            )
            
        logger.info("Saved and activated job description {id}: {title}", id=job_id, title=parsed_job.title)
        
        return {
            "id": job_id,
            "title": parsed_job.title,
            "raw_text": raw_text,
            "required_skills": parsed_job.required_skills,
            "preferred_skills": parsed_job.preferred_skills,
            "min_experience": parsed_job.min_experience,
            "seniority": parsed_job.seniority,
            "industry": parsed_job.industry,
            "employment_type": parsed_job.employment_type,
            "soft_skills": parsed_job.soft_skills,
            "created_at": created_at,
            "is_active": True,
            "hiring_profile": hiring_profile,
            "upload_metadata": upload_metadata
        }

    @staticmethod
    def get_active_job() -> Optional[Dict[str, Any]]:
        """Fetch the current active job description from the database."""
        JobRepository.create_tables()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, raw_text, required_skills, preferred_skills,
                       min_experience, seniority, industry, employment_type,
                       soft_skills, created_at, is_active, hiring_profile, upload_metadata
                FROM jobs
                WHERE is_active = 1
                LIMIT 1;
                """
            )
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return {
                "id": row["id"],
                "title": row["title"],
                "raw_text": row["raw_text"],
                "required_skills": json.loads(row["required_skills"]),
                "preferred_skills": json.loads(row["preferred_skills"]),
                "min_experience": row["min_experience"],
                "seniority": row["seniority"],
                "industry": row["industry"],
                "employment_type": row["employment_type"],
                "soft_skills": json.loads(row["soft_skills"]),
                "created_at": row["created_at"],
                "is_active": bool(row["is_active"]),
                "hiring_profile": json.loads(row["hiring_profile"]) if row["hiring_profile"] else {},
                "upload_metadata": json.loads(row["upload_metadata"]) if row["upload_metadata"] else {}
            }

    @staticmethod
    def get_history() -> List[Dict[str, Any]]:
        """Fetch a list of all job description uploads."""
        JobRepository.create_tables()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, created_at, is_active, upload_metadata
                FROM jobs
                ORDER BY created_at DESC;
                """
            )
            rows = cursor.fetchall()
            history = []
            for r in rows:
                meta = json.loads(r["upload_metadata"]) if r["upload_metadata"] else {}
                history.append({
                    "id": r["id"],
                    "title": r["title"],
                    "created_at": r["created_at"],
                    "is_active": bool(r["is_active"]),
                    "filename": meta.get("filename", "unknown"),
                    "file_size": meta.get("file_size", 0),
                    "checksum": meta.get("checksum", "")
                })
            return history

    @staticmethod
    def deactivate_all() -> None:
        """Deactivate all job profiles."""
        JobRepository.create_tables()
        with get_db_connection() as conn:
            conn.execute("UPDATE jobs SET is_active = 0;")

    @staticmethod
    def delete_current() -> bool:
        """Deactivate or remove the currently active job description."""
        JobRepository.create_tables()
        with get_db_connection() as conn:
            cursor = conn.execute("UPDATE jobs SET is_active = 0 WHERE is_active = 1;")
            return cursor.rowcount > 0
