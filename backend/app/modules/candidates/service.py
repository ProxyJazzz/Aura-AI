import gzip
import json
from datetime import date
from pathlib import Path
from typing import Iterator, Dict, Any, Tuple, List, Optional
from loguru import logger
from pydantic import ValidationError

from app.modules.candidates.schema import CandidateModel, SkillProficiency
from app.modules.candidates.repository import CandidateRepository
from app.shared.database import get_db_connection

class CandidateService:
    """Service handling business logic for candidate data parsing, validation, and analytics."""

    # Reference date for calculating last active days (matching current local time context: July 2026)
    REFERENCE_DATE = date(2026, 7, 2)

    # Keywords to detect consulting/services companies
    CONSULTING_COMPANIES = {
        "tcs", "tata consultancy", "infosys", "wipro", "accenture", "cognizant", "cts",
        "capgemini", "mindtree", "tech mahindra", "l&t", "lnt", "hcl", "wipro technologies",
        "infosys limited", "accenture solutions", "cognizant technology solutions"
    }

    # Keywords to detect AI/ML skills
    AI_ML_KEYWORDS = {
        "machine learning", "ml", "artificial intelligence", "ai", "deep learning", "nlp",
        "natural language processing", "computer vision", "cv", "reinforcement learning",
        "large language model", "llm", "transformers", "pytorch", "tensorflow", "keras",
        "scikit-learn", "sklearn", "bert", "gpt", "rag", "embeddings", "vector database",
        "pinecone", "weaviate", "qdrant", "milvus", "faiss", "neural network", "fine-tuning",
        "lora", "qlora", "gan", "speech recognition", "text-to-speech", "tts"
    }

    @staticmethod
    def stream_load_jsonl(filepath: Path) -> Iterator[str]:
        """Stream lines from a raw or gzipped JSONL file efficiently."""
        if filepath.suffix.lower() == ".gz":
            with gzip.open(filepath, "rt", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield line
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield line

    @classmethod
    def validate_record(cls, data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[CandidateModel]]:
        """Validate candidate dictionary against Pydantic CandidateModel."""
        try:
            model = CandidateModel(**data)
            return True, None, model
        except ValidationError as e:
            # Format validation errors into a single string
            errors = []
            for err in e.errors():
                loc = " -> ".join(str(l) for l in err["loc"])
                msg = err["msg"]
                errors.append(f"[{loc}]: {msg}")
            error_str = " | ".join(errors)
            return False, error_str, None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None

    @classmethod
    def detect_honeypot(cls, candidate: CandidateModel) -> bool:
        """Detect subtly impossible or inconsistent profiles (Honeypots)."""
        # 1. Expert zero duration skills check:
        # Any skill with expert proficiency and 0 duration is impossible.
        zero_duration_expert_skills = sum(
            1 for s in candidate.skills 
            if s.proficiency == SkillProficiency.EXPERT and s.duration_months == 0
        )
        if zero_duration_expert_skills >= 1:
            return True
            
        # 2. Single job exceeds total experience check:
        # A single career history role duration exceeds the candidate's total professional experience.
        total_exp_months = candidate.profile.years_of_experience * 12
        for job in candidate.career_history:
            if job.duration_months > total_exp_months + 6:
                return True
                
        # 3. Sum of all jobs exceeds total experience check:
        # The sum of all job durations exceeds total experience by more than 2 years.
        sum_durations = sum(job.duration_months for job in candidate.career_history)
        if sum_durations > total_exp_months + 24:
            return True
            
        # 4. Job date vs duration consistency check:
        # Stated duration_months does not match the actual difference between start_date and end_date.
        for job in candidate.career_history:
            try:
                start = date.fromisoformat(job.start_date)
                if job.is_current or not job.end_date:
                    end = cls.REFERENCE_DATE
                else:
                    end = date.fromisoformat(job.end_date)
                
                diff_days = (end - start).days
                expected_months = int(round(diff_days / 30.4375))
                
                if abs(expected_months - job.duration_months) > 3:
                    return True
            except Exception:
                pass
                
        return False


    @classmethod
    def is_consulting_company(cls, company_name: str) -> bool:
        """Check if a company is a services/consulting company."""
        name_lower = company_name.lower().strip()
        return any(keyword in name_lower for keyword in cls.CONSULTING_COMPANIES)

    @classmethod
    def extract_features(cls, candidate: CandidateModel) -> Dict[str, Any]:
        """Extract analytical and behavioral features from a validated candidate profile."""
        profile = candidate.profile
        signals = candidate.redrob_signals
        
        # ── Skills features ──────────────────────────────────────────
        skill_names = [s.name for s in candidate.skills]
        skills_list = ", ".join(skill_names)
        primary_skills_count = len(skill_names)
        
        # Check for AI/ML skills
        has_ai_ml_skills = 0
        for name in skill_names:
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in cls.AI_ML_KEYWORDS):
                has_ai_ml_skills = 1
                break
                
        # ── Experience features ──────────────────────────────────────
        years_of_experience = profile.years_of_experience
        
        # Consulting firm checks
        worked_companies = [job.company for job in candidate.career_history]
        consulting_flags = [cls.is_consulting_company(c) for c in worked_companies]
        
        has_worked_in_consulting = 1 if any(consulting_flags) else 0
        has_only_consulting_experience = 1 if (consulting_flags and all(consulting_flags)) else 0
        
        num_companies = len(set(worked_companies))
        
        # Calculate tenure stats
        durations = [job.duration_months for job in candidate.career_history]
        avg_tenure_months = sum(durations) / len(durations) if durations else 0.0
        
        is_currently_employed = 1 if any(job.is_current for job in candidate.career_history) else 0
        
        # ── Education features ───────────────────────────────────────
        highest_tier = "unknown"
        tier_values = {"tier_1": 1, "tier_2": 2, "tier_3": 3, "tier_4": 4, "unknown": 5}
        
        has_masters_or_phd = 0
        
        for edu in candidate.education:
            # Find the best tier (lowest value represents highest prestige)
            current_tier = edu.tier.value if hasattr(edu.tier, 'value') else str(edu.tier)
            if tier_values.get(current_tier, 5) < tier_values.get(highest_tier, 5):
                highest_tier = current_tier
                
            deg_lower = edu.degree.lower()
            if any(term in deg_lower for term in ["m.s.", "ms", "m.sc", "msc", "m.e.", "me", "m.tech", "mtech", "ph.d", "phd", "mba"]):
                has_masters_or_phd = 1
                
        # ── Certifications & Languages ───────────────────────────────
        num_certifications = len(candidate.certifications)
        num_languages = len(candidate.languages)
        
        # ── Behavioral features ──────────────────────────────────────
        profile_completeness_score = signals.profile_completeness_score
        recruiter_response_rate = signals.recruiter_response_rate
        avg_response_time_hours = signals.avg_response_time_hours
        open_to_work_flag = 1 if signals.open_to_work_flag else 0
        github_activity_score = signals.github_activity_score
        interview_completion_rate = signals.interview_completion_rate
        offer_acceptance_rate = signals.offer_acceptance_rate
        
        # Calculate recency of last active date
        last_active_date_str = signals.last_active_date
        try:
            last_active = date.fromisoformat(last_active_date_str)
            last_active_days_ago = (cls.REFERENCE_DATE - last_active).days
        except Exception:
            last_active_days_ago = 999
            
        # Detect if candidate is a honeypot
        is_honeypot = 1 if cls.detect_honeypot(candidate) else 0

        return {
            "candidate_id": candidate.candidate_id,
            "is_valid": 1,
            "is_honeypot": is_honeypot,
            "validation_error": None,
            "raw_json": json.dumps(candidate.model_dump()),
            
            # Features
            "anonymized_name": profile.anonymized_name,
            "location": profile.location,
            "country": profile.country,
            "years_of_experience": years_of_experience,
            "current_title": profile.current_title,
            "current_company": profile.current_company,
            "profile_completeness_score": profile_completeness_score,
            "recruiter_response_rate": recruiter_response_rate,
            "avg_response_time_hours": avg_response_time_hours,
            "open_to_work_flag": open_to_work_flag,
            "skills_list": skills_list,
            "primary_skills_count": primary_skills_count,
            "has_ai_ml_skills": has_ai_ml_skills,
            "has_only_consulting_experience": has_only_consulting_experience,
            "has_worked_in_consulting": has_worked_in_consulting,
            "num_companies": num_companies,
            "avg_tenure_months": avg_tenure_months,
            "highest_education_tier": highest_tier,
            "has_masters_or_phd": has_masters_or_phd,
            "num_certifications": num_certifications,
            "num_languages": num_languages,
            "last_active_date": last_active_date_str
        }

    @classmethod
    def process_and_save_candidate(cls, data: Dict[str, Any]) -> Tuple[bool, bool, Optional[str]]:
        """Validate, extract features, and save candidate. Returns (is_valid, is_honeypot, error_message)."""
        is_valid, err_msg, candidate = cls.validate_record(data)
        
        if not is_valid:
            # Save malformed candidate record for logging/audit
            candidate_id = data.get("candidate_id", "MALFORMED_CAND")
            malformed_record = {
                "candidate_id": candidate_id,
                "is_valid": 0,
                "is_honeypot": 0,
                "validation_error": err_msg,
                "raw_json": json.dumps(data)
            }
            CandidateRepository.insert_candidates_batch([malformed_record])
            return False, False, err_msg
            
        # Extract features and save
        features = cls.extract_features(candidate)
        CandidateRepository.insert_candidates_batch([features])
        return True, bool(features["is_honeypot"]), None

    @classmethod
    def calculate_global_statistics(cls) -> Dict[str, Any]:
        """Calculate aggregate dataset statistics using SQL queries."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Counts
            cursor.execute("SELECT COUNT(*) FROM candidates;")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM candidates WHERE is_valid = 1;")
            valid = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM candidates WHERE is_valid = 0;")
            malformed = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM candidates WHERE is_honeypot = 1;")
            honeypot = cursor.fetchone()[0]
            
            if valid == 0:
                return {
                    "total_candidates": total,
                    "valid_candidates": valid,
                    "malformed_candidates": malformed,
                    "honeypot_candidates": honeypot,
                    "experience_distribution": {},
                    "education_tier_distribution": {},
                    "top_skills": [],
                    "top_industries": [],
                    "open_to_work_percentage": 0.0,
                    "avg_profile_completeness": 0.0,
                    "avg_recruiter_response_rate": 0.0
                }

            # Experience distribution
            cursor.execute("""
                SELECT 
                    MIN(years_of_experience), 
                    MAX(years_of_experience), 
                    AVG(years_of_experience) 
                FROM candidates WHERE is_valid = 1;
            """)
            min_exp, max_exp, avg_exp = cursor.fetchone()
            
            # Median experience
            cursor.execute("""
                SELECT years_of_experience FROM candidates 
                WHERE is_valid = 1 
                ORDER BY years_of_experience 
                LIMIT 1 OFFSET (SELECT COUNT(*) FROM candidates WHERE is_valid = 1) / 2;
            """)
            row = cursor.fetchone()
            median_exp = row[0] if row else 0.0
            
            # Buckets
            buckets = {"0-2": 0, "3-5": 0, "6-9": 0, "10-15": 0, "16+": 0}
            cursor.execute("""
                SELECT years_of_experience, COUNT(*) 
                FROM candidates WHERE is_valid = 1 
                GROUP BY 
                    CASE 
                        WHEN years_of_experience < 3.0 THEN '0-2'
                        WHEN years_of_experience < 6.0 THEN '3-5'
                        WHEN years_of_experience < 10.0 THEN '6-9'
                        WHEN years_of_experience < 16.0 THEN '10-15'
                        ELSE '16+'
                    END;
            """)
            for bucket_key, count in cursor.fetchall():
                if bucket_key in buckets:
                    buckets[bucket_key] = count
                    
            # Education Tier Distribution
            cursor.execute("""
                SELECT highest_education_tier, COUNT(*) 
                FROM candidates WHERE is_valid = 1 
                GROUP BY highest_education_tier;
            """)
            education_tier_dist = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Top Industries
            cursor.execute("""
                SELECT current_industry, COUNT(*) as count 
                FROM (
                    SELECT json_extract(raw_json, '$.profile.current_industry') as current_industry 
                    FROM candidates WHERE is_valid = 1
                )
                WHERE current_industry IS NOT NULL AND current_industry != ''
                GROUP BY current_industry 
                ORDER BY count DESC 
                LIMIT 10;
            """)
            top_industries = [{"industry": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Behavioral Signals summary
            cursor.execute("""
                SELECT 
                    AVG(open_to_work_flag) * 100, 
                    AVG(profile_completeness_score), 
                    AVG(recruiter_response_rate) 
                FROM candidates WHERE is_valid = 1;
            """)
            open_to_work_pct, avg_completeness, avg_response = cursor.fetchone()
            
            # Top Skills (Splitting comma list in Python)
            # Since skills_list is a string "Python, React, etc.", we fetch all skills_list and aggregate in memory
            # Given WAL and streaming, we can do this fast. Let's fetch all skills lists.
            cursor.execute("SELECT skills_list FROM candidates WHERE is_valid = 1;")
            skill_counts = {}
            for (skills_str,) in cursor.fetchall():
                if skills_str:
                    for s in skills_str.split(", "):
                        skill_counts[s] = skill_counts.get(s, 0) + 1
                        
            top_skills = sorted(
                [{"skill": k, "count": v} for k, v in skill_counts.items()],
                key=lambda x: x["count"],
                reverse=True
            )[:15]

            return {
                "total_candidates": total,
                "valid_candidates": valid,
                "malformed_candidates": malformed,
                "honeypot_candidates": honeypot,
                "experience_distribution": {
                    "min": float(min_exp or 0.0),
                    "max": float(max_exp or 0.0),
                    "avg": round(float(avg_exp or 0.0), 2),
                    "median": float(median_exp or 0.0),
                    "buckets": buckets
                },
                "education_tier_distribution": education_tier_dist,
                "top_skills": top_skills,
                "top_industries": top_industries,
                "open_to_work_percentage": round(float(open_to_work_pct or 0.0), 2),
                "avg_profile_completeness": round(float(avg_completeness or 0.0), 2),
                "avg_recruiter_response_rate": round(float(avg_response or 0.0), 4)
            }
