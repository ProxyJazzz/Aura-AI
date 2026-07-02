from typing import List, Dict, Any
from app.modules.intelligence.schema import MarketIntelligence
import json

class MarketInsightsEngine:
    """Aggregates market intelligence from candidate data."""

    @classmethod
    def evaluate(cls, candidates: List[Dict[str, Any]]) -> MarketIntelligence:
        companies = {}
        universities = {}
        certifications = {}
        skills = {}
        languages = {}

        for c in candidates:
            # Experience / Companies
            exp_data = c.get("experience", "[]")
            if isinstance(exp_data, str):
                try:
                    exp_list = json.loads(exp_data)
                    for exp in exp_list:
                        comp = exp.get("company")
                        if comp:
                            companies[comp] = companies.get(comp, 0) + 1
                except Exception:
                    pass

            # Education / Universities
            edu_data = c.get("education", "[]")
            if isinstance(edu_data, str):
                try:
                    edu_list = json.loads(edu_data)
                    for edu in edu_list:
                        inst = edu.get("institution")
                        if inst:
                            universities[inst] = universities.get(inst, 0) + 1
                except Exception:
                    pass

            # Skills
            skill_data = c.get("skills", "[]")
            if isinstance(skill_data, str):
                try:
                    skill_list = json.loads(skill_data)
                    for s in skill_list:
                        name = s.get("name") if isinstance(s, dict) else s
                        if name:
                            skills[name] = skills.get(name, 0) + 1
                except Exception:
                    pass

        def get_top(data: dict, limit: int = 5) -> List[str]:
            sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
            return [k for k, v in sorted_items[:limit]]

        return MarketIntelligence(
            top_skills=get_top(skills),
            top_universities=get_top(universities),
            top_companies=get_top(companies),
            top_languages=["English", "Spanish"] # Placeholder as languages might not be heavily extracted yet
        )
