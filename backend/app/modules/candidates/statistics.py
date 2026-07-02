from typing import Dict, Any
from app.shared.database import get_db_connection

class CandidateStatistics:
    """Generates statistics summary from the candidates SQLite database."""

    @classmethod
    def calculate(cls) -> Dict[str, Any]:
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
                    "experience_distribution": {
                        "min": 0.0,
                        "max": 0.0,
                        "avg": 0.0,
                        "median": 0.0,
                        "buckets": {"0-2": 0, "3-5": 0, "6-9": 0, "10-15": 0, "16+": 0}
                    },
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
                SELECT 
                    CASE 
                        WHEN years_of_experience < 3.0 THEN '0-2'
                        WHEN years_of_experience < 6.0 THEN '3-5'
                        WHEN years_of_experience < 10.0 THEN '6-9'
                        WHEN years_of_experience < 16.0 THEN '10-15'
                        ELSE '16+'
                    END as bucket,
                    COUNT(*)
                FROM candidates WHERE is_valid = 1 
                GROUP BY bucket;
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
            
            # Top Skills
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
