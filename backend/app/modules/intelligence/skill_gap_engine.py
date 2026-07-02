from typing import List, Dict, Any
from app.modules.intelligence.schema import SkillGapIntelligence
import json

class SkillGapEngine:
    """Computes skill coverage and identifies gaps based on raw candidate data."""

    @classmethod
    def evaluate(cls, candidates: List[Dict[str, Any]]) -> SkillGapIntelligence:
        if not candidates:
            return SkillGapIntelligence(
                missing_skills=["No data"],
                high_demand_skills=["No data"],
                skill_coverage=0.0
            )

        all_skills = {}
        for c in candidates:
            skills = c.get("skills", [])
            # Handle if stored as JSON string
            if isinstance(skills, str):
                try:
                    skills = json.loads(skills)
                except Exception:
                    skills = []
            
            for s in skills:
                name = s.get("name") if isinstance(s, dict) else s
                if name:
                    all_skills[name] = all_skills.get(name, 0) + 1

        # Calculate high demand (most frequent skills present)
        sorted_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)
        high_demand = [k for k, v in sorted_skills[:5]]
        
        # We can't know missing skills definitively without the job profile in this exact context,
        # but we can simulate deterministic logic: skills that are extremely rare in the pool.
        missing = [k for k, v in sorted_skills[-5:] if v == 1]

        # Skill coverage: arbitrary deterministic metric for demonstration (percentage of pool having top skills)
        top_skill_count = sum(v for k, v in sorted_skills[:3])
        total_skills_count = sum(all_skills.values()) if all_skills else 1
        coverage = min(100.0, round((top_skill_count / total_skills_count) * 100 * 2, 2))

        return SkillGapIntelligence(
            missing_skills=missing,
            high_demand_skills=high_demand,
            skill_coverage=coverage
        )
