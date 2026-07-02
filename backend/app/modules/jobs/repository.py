import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from loguru import logger

from app.shared.database import get_db_connection
from app.modules.jobs.schema import JobModel

class JobRepository:
    """Repository handling SQLite operations for job profiles."""

    @staticmethod
    def create_tables():
        """Create the jobs table and associated indexes if they do not exist."""
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    raw_text TEXT NOT NULL,
                    required_skills TEXT NOT NULL, -- JSON array
                    preferred_skills TEXT NOT NULL, -- JSON array
                    min_experience REAL NOT NULL,
                    seniority TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    employment_type TEXT NOT NULL,
                    soft_skills TEXT NOT NULL, -- JSON array
                    created_at TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 0
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active);")
            logger.info("Jobs table initialized successfully.")

    @staticmethod
    def save_job(raw_text: str, parsed_job: JobModel) -> Dict[str, Any]:
        """
        Deactivate previous jobs, save the new job profile as active, and return saved details.
        """
        # Ensure table exists
        JobRepository.create_tables()
        
        job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        
        # Serialize list fields to JSON strings
        req_skills_json = json.dumps(parsed_job.required_skills)
        pref_skills_json = json.dumps(parsed_job.preferred_skills)
        soft_skills_json = json.dumps(parsed_job.soft_skills)
        
        with get_db_connection() as conn:
            # Deactivate all existing jobs
            conn.execute("UPDATE jobs SET is_active = 0;")
            
            # Insert the new active job
            conn.execute(
                """
                INSERT INTO jobs (
                    id, title, raw_text, required_skills, preferred_skills,
                    min_experience, seniority, industry, employment_type,
                    soft_skills, created_at, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
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
                    created_at
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
            "is_active": True
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
                       soft_skills, created_at, is_active
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
                "is_active": bool(row["is_active"])
            }
