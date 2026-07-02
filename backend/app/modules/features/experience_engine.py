import json
from typing import Dict, Any, Tuple
from app.modules.features.base_engine import BaseFeatureEngine

class ExperienceEngine(BaseFeatureEngine):
    """
    Experience Intelligence Engine.
    Evaluates:
    1. Years of experience vs Job requirements (35 pts)
    2. Current role relevance to Job title (20 pts)
    3. Leadership keywords in current/past titles (15 pts)
    4. Title career progression over history (10 pts)
    5. Company type quality (avoiding services-only firms) (10 pts)
    6. Employment tenure stability (10 pts)
    """

    def _run_calculation(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # 1. Base experience stats
        cand_exp = float(candidate.get("years_of_experience") or 0.0)
        job_min_exp = float(job.get("min_experience") or 0.0)
        
        # Dimension A: Years of Experience (Max 35 points)
        if job_min_exp <= 0.0:
            exp_points = 35.0
        elif cand_exp >= job_min_exp:
            # Full points + bonus up to 35 max
            exp_points = 35.0
        else:
            # Linear scaling
            exp_points = (cand_exp / job_min_exp) * 35.0
            
        # Dimension B: Role Relevance (Max 20 points)
        # Token overlap check between job title and current title
        job_title = job.get("title", "").strip().lower()
        cand_title = candidate.get("current_title", "").strip().lower()
        
        role_points = 0.0
        if job_title == cand_title:
            role_points = 20.0
        else:
            job_tokens = set(t for t in job_title.split() if len(t) > 2)
            cand_tokens = set(t for t in cand_title.split() if len(t) > 2)
            overlap = job_tokens.intersection(cand_tokens)
            if overlap:
                # Partial overlap
                role_points = min(20.0, 10.0 + (len(overlap) * 5.0))
                
        # Dimension C: Leadership (Max 15 points)
        leadership_keywords = {"lead", "head", "manager", "architect", "founding", "director", "chief", "principal", "staff"}
        has_leadership = False
        
        # Check current title
        if any(k in cand_title for k in leadership_keywords):
            has_leadership = True
            
        # Check past titles in career history
        raw_json_str = candidate.get("raw_json")
        past_titles = []
        if raw_json_str:
            try:
                raw_data = json.loads(raw_json_str)
                career_history = raw_data.get("career_history", [])
                for past_job in career_history:
                    p_title = past_job.get("title", "").lower()
                    past_titles.append(p_title)
                    if any(k in p_title for k in leadership_keywords):
                        has_leadership = True
            except Exception:
                pass
                
        leadership_points = 15.0 if has_leadership else 0.0
        
        # Dimension D: Career Progression (Max 10 points)
        # Check if they went from Junior/Associate to Senior/Lead/Staff over history
        progression_points = 0.0
        junior_prefixes = {"junior", "jr", "associate", "intern", "trainee"}
        senior_prefixes = {"senior", "sr", "lead", "staff", "principal", "architect", "manager"}
        
        has_junior_past = any(any(pref in t for pref in junior_prefixes) for t in past_titles)
        has_senior_current = any(pref in cand_title for pref in senior_prefixes)
        
        if has_junior_past and has_senior_current:
            progression_points = 10.0
        elif has_senior_current:
            # Stated directly as senior/lead
            progression_points = 7.0
        else:
            progression_points = 3.0
            
        # Dimension E: Company Quality (Max 10 points)
        # Full points if not purely consulting/services companies
        has_only_consulting = bool(candidate.get("has_only_consulting_experience") or False)
        company_quality_points = 0.0 if has_only_consulting else 10.0
        
        # Dimension F: Employment Stability (Max 10 points)
        avg_tenure = float(candidate.get("avg_tenure_months") or 0.0)
        if avg_tenure >= 24.0:
            stability_points = 10.0
        elif avg_tenure >= 12.0:
            stability_points = 5.0
        else:
            stability_points = 0.0  # Job switching penalty
            
        # Sum final score
        final_score = (
            exp_points + 
            role_points + 
            leadership_points + 
            progression_points + 
            company_quality_points + 
            stability_points
        )
        
        metadata = {
            "years_of_experience": cand_exp,
            "min_experience_required": job_min_exp,
            "current_title": candidate.get("current_title", ""),
            "average_tenure_months": avg_tenure,
            "is_services_only": has_only_consulting,
            "reasoning": (
                f"Candidate has {cand_exp:.1f} years of experience vs job requirement of {job_min_exp:.1f} years. "
                f"Role relevance score is {role_points:.1f}/20. "
                f"Employment stability average tenure is {avg_tenure:.1f} months."
            )
        }
        
        return final_score, metadata
