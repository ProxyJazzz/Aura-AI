import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from app.shared.database import get_db_connection

class CandidateRepository:
    """Repository responsible for database operations on candidates and statistics."""

    @staticmethod
    def create_tables() -> None:
        """Create the candidates and dataset_statistics tables in SQLite."""
        with get_db_connection() as conn:
            # Create candidates table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    candidate_id TEXT PRIMARY KEY,
                    is_valid INTEGER NOT NULL,
                    is_honeypot INTEGER NOT NULL,
                    validation_error TEXT,
                    raw_json TEXT NOT NULL,
                    
                    -- Extracted Features
                    anonymized_name TEXT,
                    location TEXT,
                    country TEXT,
                    years_of_experience REAL,
                    current_title TEXT,
                    current_company TEXT,
                    profile_completeness_score REAL,
                    recruiter_response_rate REAL,
                    avg_response_time_hours REAL,
                    open_to_work_flag INTEGER,
                    skills_list TEXT,
                    primary_skills_count INTEGER,
                    has_ai_ml_skills INTEGER,
                    has_only_consulting_experience INTEGER,
                    has_worked_in_consulting INTEGER,
                    num_companies INTEGER,
                    avg_tenure_months REAL,
                    highest_education_tier TEXT,
                    has_masters_or_phd INTEGER,
                    num_certifications INTEGER,
                    num_languages INTEGER,
                    last_active_date TEXT
                );
            """)
            
            # Create indexes for fast filtering and sorting
            conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_is_valid ON candidates(is_valid);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_is_honeypot ON candidates(is_honeypot);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_experience ON candidates(years_of_experience);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_open_to_work ON candidates(open_to_work_flag);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_location ON candidates(location);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_skills ON candidates(skills_list);")
            
            # Create statistics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dataset_statistics (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
            
            logger.info("Database tables and indexes created successfully.")

    @staticmethod
    def insert_candidates_batch(batch: List[Dict[str, Any]]) -> None:
        """Insert a batch of candidates using executemany for high performance."""
        query = """
            INSERT INTO candidates (
                candidate_id, is_valid, is_honeypot, validation_error, raw_json,
                anonymized_name, location, country, years_of_experience,
                current_title, current_company, profile_completeness_score,
                recruiter_response_rate, avg_response_time_hours, open_to_work_flag,
                skills_list, primary_skills_count, has_ai_ml_skills,
                has_only_consulting_experience, has_worked_in_consulting,
                num_companies, avg_tenure_months, highest_education_tier,
                has_masters_or_phd, num_certifications, num_languages, last_active_date
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?
            ) ON CONFLICT(candidate_id) DO UPDATE SET
                is_valid=excluded.is_valid,
                is_honeypot=excluded.is_honeypot,
                validation_error=excluded.validation_error,
                raw_json=excluded.raw_json,
                anonymized_name=excluded.anonymized_name,
                location=excluded.location,
                country=excluded.country,
                years_of_experience=excluded.years_of_experience,
                current_title=excluded.current_title,
                current_company=excluded.current_company,
                profile_completeness_score=excluded.profile_completeness_score,
                recruiter_response_rate=excluded.recruiter_response_rate,
                avg_response_time_hours=excluded.avg_response_time_hours,
                open_to_work_flag=excluded.open_to_work_flag,
                skills_list=excluded.skills_list,
                primary_skills_count=excluded.primary_skills_count,
                has_ai_ml_skills=excluded.has_ai_ml_skills,
                has_only_consulting_experience=excluded.has_only_consulting_experience,
                has_worked_in_consulting=excluded.has_worked_in_consulting,
                num_companies=excluded.num_companies,
                avg_tenure_months=excluded.avg_tenure_months,
                highest_education_tier=excluded.highest_education_tier,
                has_masters_or_phd=excluded.has_masters_or_phd,
                num_certifications=excluded.num_certifications,
                num_languages=excluded.num_languages,
                last_active_date=excluded.last_active_date;
        """
        params = []
        for c in batch:
            params.append((
                c["candidate_id"], c["is_valid"], c["is_honeypot"], c.get("validation_error"), c["raw_json"],
                c.get("anonymized_name"), c.get("location"), c.get("country"), c.get("years_of_experience"),
                c.get("current_title"), c.get("current_company"), c.get("profile_completeness_score"),
                c.get("recruiter_response_rate"), c.get("avg_response_time_hours"), c.get("open_to_work_flag"),
                c.get("skills_list"), c.get("primary_skills_count"), c.get("has_ai_ml_skills"),
                c.get("has_only_consulting_experience"), c.get("has_worked_in_consulting"),
                c.get("num_companies"), c.get("avg_tenure_months"), c.get("highest_education_tier"),
                c.get("has_masters_or_phd"), c.get("num_certifications"), c.get("num_languages"), c.get("last_active_date")
            ))
            
        with get_db_connection() as conn:
            conn.executemany(query, params)

    @staticmethod
    def get_candidates(
        skill: Optional[str] = None,
        min_experience: Optional[float] = None,
        max_experience: Optional[float] = None,
        open_to_work: Optional[bool] = None,
        location: Optional[str] = None,
        is_valid: Optional[bool] = None,
        is_honeypot: Optional[bool] = None,
        sort_by: str = "candidate_id",
        sort_order: str = "asc",
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Query candidates with filters, sorting, and pagination. Returns (candidates, total_count)."""
        base_query = "FROM candidates WHERE 1=1"
        params = []
        
        if skill:
            base_query += " AND skills_list LIKE ?"
            params.append(f"%{skill}%")
            
        if min_experience is not None:
            base_query += " AND years_of_experience >= ?"
            params.append(min_experience)
            
        if max_experience is not None:
            base_query += " AND years_of_experience <= ?"
            params.append(max_experience)
            
        if open_to_work is not None:
            base_query += " AND open_to_work_flag = ?"
            params.append(1 if open_to_work else 0)
            
        if location:
            base_query += " AND location LIKE ?"
            params.append(f"%{location}%")
            
        if is_valid is not None:
            base_query += " AND is_valid = ?"
            params.append(1 if is_valid else 0)
            
        if is_honeypot is not None:
            base_query += " AND is_honeypot = ?"
            params.append(1 if is_honeypot else 0)

        # Count query
        count_query = f"SELECT COUNT(*) {base_query}"
        
        # Validation for sort fields to prevent SQL injection
        allowed_sort_fields = {
            "candidate_id", "years_of_experience", "profile_completeness_score",
            "recruiter_response_rate", "avg_response_time_hours", "num_companies"
        }
        if sort_by not in allowed_sort_fields:
            sort_by = "candidate_id"
            
        order = "DESC" if sort_order.lower() == "desc" else "ASC"
        
        # Select query
        select_query = f"""
            SELECT candidate_id, is_valid, is_honeypot, validation_error, raw_json,
                   anonymized_name, location, country, years_of_experience,
                   current_title, current_company, profile_completeness_score,
                   recruiter_response_rate, avg_response_time_hours, open_to_work_flag,
                   skills_list, primary_skills_count, has_ai_ml_skills,
                   has_only_consulting_experience, has_worked_in_consulting,
                   num_companies, avg_tenure_months, highest_education_tier,
                   has_masters_or_phd, num_certifications, num_languages, last_active_date
            {base_query}
            ORDER BY {sort_by} {order}
            LIMIT ? OFFSET ?
        """
        
        select_params = params + [limit, offset]
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            cursor.execute(select_query, select_params)
            rows = cursor.fetchall()
            
            candidates = []
            for row in rows:
                candidates.append(dict(row))
                
            return candidates, total_count

    @staticmethod
    def get_candidate_by_id(candidate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single candidate by their unique candidate_id."""
        query = "SELECT * FROM candidates WHERE candidate_id = ?"
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (candidate_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    @staticmethod
    def save_statistics(stats: Dict[str, Any]) -> None:
        """Cache precalculated statistics."""
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO dataset_statistics (key, value) VALUES ('summary', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (json.dumps(stats),)
            )

    @staticmethod
    def get_statistics() -> Optional[Dict[str, Any]]:
        """Retrieve cached statistics."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM dataset_statistics WHERE key = 'summary'")
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    @staticmethod
    def get_candidates_by_ids(candidate_ids: List[str]) -> List[Dict[str, Any]]:
        """Retrieve details for a list of candidate IDs in a single query."""
        if not candidate_ids:
            return []
        placeholders = ",".join("?" for _ in candidate_ids)
        query = f"SELECT * FROM candidates WHERE candidate_id IN ({placeholders})"
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, candidate_ids)
            return [dict(row) for row in cursor.fetchall()]
