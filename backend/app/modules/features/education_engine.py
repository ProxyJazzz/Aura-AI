import json
from typing import Dict, Any, Tuple
from app.modules.features.base_engine import BaseFeatureEngine

class EducationEngine(BaseFeatureEngine):
    """
    Education Intelligence Engine.
    Evaluates:
    1. Highest Institution Tier (Max 50 points)
    2. Degree Level (Bachelor, Master, PhD) (Max 25 points)
    3. Relevant Field of Study (STEM/CS/AI) (Max 15 points)
    4. Research background (thesis/publications) (Max 10 points)
    """

    def _run_calculation(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # 1. Institution Tier (Max 50 points)
        tier_str = str(candidate.get("highest_education_tier") or "unknown").lower()
        
        tier_points = 10.0  # Default Unknown
        if "tier_1" in tier_str:
            tier_points = 50.0
        elif "tier_2" in tier_str:
            tier_points = 40.0
        elif "tier_3" in tier_str:
            tier_points = 30.0
        elif "tier_4" in tier_str:
            tier_points = 20.0
            
        # 2. Parse raw education details for degree level & field of study
        raw_json_str = candidate.get("raw_json")
        has_masters_or_phd = bool(candidate.get("has_masters_or_phd") or False)
        
        is_phd = False
        is_masters = has_masters_or_phd
        has_stem_branch = False
        has_research = False
        
        degrees = []
        fields_of_study = []
        
        if raw_json_str:
            try:
                raw_data = json.loads(raw_json_str)
                education_history = raw_data.get("education", [])
                for edu in education_history:
                    deg = edu.get("degree", "").lower()
                    field = edu.get("field_of_study", "").lower()
                    grade = edu.get("grade", "").lower() if edu.get("grade") else ""
                    
                    degrees.append(deg)
                    fields_of_study.append(field)
                    
                    # Detect PhD
                    if "phd" in deg or "ph.d" in deg or "doctor" in deg:
                        is_phd = True
                        
                    # STEM/CS Branch Overlaps
                    stem_keywords = {
                        "computer science", "computer engineering", "software engineering", 
                        "information technology", "data science", "machine learning",
                        "artificial intelligence", "mathematics", "statistics", "electrical", "physics"
                    }
                    if any(k in field for k in stem_keywords):
                        has_stem_branch = True
                        
                    # Research indicators (thesis/research assistant/publications)
                    research_keywords = {"research", "thesis", "publication", "fellowship", "dissertation"}
                    if any(k in deg or k in field or k in grade for k in research_keywords):
                        has_research = True
            except Exception:
                pass
                
        # Degree Level Points (Max 25 points)
        degree_points = 15.0  # Default Bachelor's/Other
        if is_phd:
            degree_points = 25.0
        elif is_masters:
            degree_points = 20.0
            
        # Field of Study Relevance Points (Max 15 points)
        branch_points = 15.0 if has_stem_branch else 5.0
        
        # Research Background Points (Max 10 points)
        research_points = 10.0 if has_research else 0.0
        
        # Sum final score
        final_score = tier_points + degree_points + branch_points + research_points
        
        metadata = {
            "highest_tier": tier_str.upper(),
            "has_masters_or_phd": has_masters_or_phd,
            "is_phd_holder": is_phd,
            "is_stem_aligned": has_stem_branch,
            "has_research_background": has_research,
            "degrees": degrees,
            "fields_of_study": fields_of_study
        }
        
        return final_score, metadata
