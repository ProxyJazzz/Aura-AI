import json
from typing import Dict, Any, Tuple, List
from app.modules.features.base_engine import BaseFeatureEngine

class LanguageEngine(BaseFeatureEngine):
    """
    Language Intelligence Engine.
    Evaluates:
    1. Programming languages (Python, Go, Java, C++, TypeScript, SQL, Rust, C#, Kotlin, Swift) (Max 60 points)
    2. Human languages (Native, Professional, Conversational fluencies) (Max 40 points)
    """

    def _run_calculation(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # 1. Programming Languages (Max 60 points)
        prog_languages_set = {
            "python", "go", "golang", "rust", "c++", "cpp", "java", "scala", "c#", "csharp",
            "typescript", "javascript", "ts", "js", "kotlin", "swift", "ruby", "php"
        }
        
        cand_skills_str = candidate.get("skills_list", "")
        cand_skills = {s.strip().lower() for s in cand_skills_str.split(",") if s.strip()}
        
        matched_prog_languages = prog_languages_set.intersection(cand_skills)
        
        # Each matching programming language is 20 points, capped at 60
        prog_points = min(60.0, len(matched_prog_languages) * 20.0)
        
        # 2. Human Languages (Max 40 points)
        raw_json_str = candidate.get("raw_json")
        human_langs: List[Dict[str, Any]] = []
        
        if raw_json_str:
            try:
                raw_data = json.loads(raw_json_str)
                human_langs = raw_data.get("languages", [])
            except Exception:
                pass
                
        has_english_prof = False
        other_languages_count = 0
        human_langs_summary = []
        
        for item in human_langs:
            lang = item.get("language", "").strip()
            prof = str(item.get("proficiency", "")).lower()
            
            human_langs_summary.append(f"{lang} ({prof})")
            
            is_fluent = any(p in prof for p in ["native", "professional", "conversational", "fluent"])
            
            if lang.lower() == "english" and is_fluent:
                has_english_prof = True
            elif is_fluent:
                other_languages_count += 1
                
        # English fluency: 25 points
        # Other fluent languages: 15 points per language, up to 40 max
        human_points = 0.0
        if has_english_prof:
            human_points += 25.0
            
        human_points += min(15.0, other_languages_count * 15.0)
        human_points = min(40.0, human_points)
        
        # If no human languages are defined in raw JSON, fallback to a base score (e.g. 25 points)
        # assuming basic English communication since they are registered on the platform.
        if not human_langs:
            human_points = 25.0
            
        final_score = prog_points + human_points
        
        metadata = {
            "programming_languages_matched": sorted(list(matched_prog_languages)),
            "human_languages_found": human_langs_summary,
            "has_english_fluency": has_english_prof or not human_langs
        }
        
        return final_score, metadata
