from typing import Dict, Any, Tuple, Set
from app.modules.features.base_engine import BaseFeatureEngine

class SkillEngine(BaseFeatureEngine):
    """
    Skill Intelligence Engine.
    Compares candidate skills against job required and preferred skills.
    Calculates coverage percentages and a weighted final skill score.
    """

    def _run_calculation(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # 1. Parse job skills (clean and case-normalize)
        req_skills_list = job.get("required_skills", [])
        pref_skills_list = job.get("preferred_skills", [])
        
        required_set = {s.strip().lower() for s in req_skills_list if s.strip()}
        preferred_set = {s.strip().lower() for s in pref_skills_list if s.strip()}
        
        # 2. Parse candidate skills
        # candidate["skills_list"] is a comma-separated string e.g. "Python, PyTorch, Sql"
        cand_skills_str = candidate.get("skills_list", "")
        cand_skills = {s.strip().lower() for s in cand_skills_str.split(",") if s.strip()}
        
        # 3. Compute skill overlaps
        matched_required = required_set.intersection(cand_skills)
        missing_required = required_set.difference(cand_skills)
        
        matched_preferred = preferred_set.intersection(cand_skills)
        missing_preferred = preferred_set.difference(cand_skills)
        
        # Additional skills: candidate skills that are neither required nor preferred
        all_requested = required_set.union(preferred_set)
        additional_skills = cand_skills.difference(all_requested)
        
        # Convert sets back to sorted lists using original job casing where possible
        # Helper to map lowercase sets back to clean list representation
        req_mapped = [s for s in req_skills_list if s.lower() in matched_required]
        req_missing_mapped = [s for s in req_skills_list if s.lower() in missing_required]
        
        pref_mapped = [s for s in pref_skills_list if s.lower() in matched_preferred]
        pref_missing_mapped = [s for s in pref_skills_list if s.lower() in missing_preferred]
        
        # Map additional skills (preserves original casing from candidate string)
        cand_skills_cased = [s.strip() for s in cand_skills_str.split(",") if s.strip()]
        add_mapped = [s for s in cand_skills_cased if s.lower() in additional_skills]
        
        # 4. Score logic
        # Required skills = 80% weight, Preferred skills = 20% weight
        if required_set:
            required_score = (len(matched_required) / len(required_set)) * 100.0
            coverage = (len(matched_required) / len(required_set)) * 100.0
        else:
            required_score = 100.0
            coverage = 100.0
            
        if preferred_set:
            preferred_score = (len(matched_preferred) / len(preferred_set)) * 100.0
            score = (required_score * 0.8) + (preferred_score * 0.2)
        else:
            preferred_score = 100.0
            score = required_score
            
        metadata = {
            "matched_required": sorted(req_mapped),
            "missing_required": sorted(req_missing_mapped),
            "matched_preferred": sorted(pref_mapped),
            "missing_preferred": sorted(pref_missing_mapped),
            "additional_skills": sorted(add_mapped),
            "coverage": round(coverage, 2)
        }
        
        return score, metadata
