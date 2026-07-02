from typing import Dict, Any
from app.modules.ranking.normalization_engine import NormalizationEngine

class AggregationEngine:
    """Computes overall weighted score scorecard values."""

    @classmethod
    def compute_overall_score(cls, features: Dict[str, Any], weights: Dict[str, float]) -> float:
        """
        Calculates the weighted sum of candidate features.
        """
        semantic = float(features.get("semantic_score", 0.0))
        skills = float(features.get("skill_score", 0.0))
        experience = float(features.get("experience_score", 0.0))
        education = float(features.get("education_score", 0.0))
        certification = float(features.get("certification_score", 0.0))
        language = float(features.get("language_score", 0.0))
        behavior = float(features.get("behavior_score", 0.0))

        overall_score = (
            semantic * weights.get("semantic", 0.0) +
            skills * weights.get("skills", 0.0) +
            experience * weights.get("experience", 0.0) +
            education * weights.get("education", 0.0) +
            certification * weights.get("certification", 0.0) +
            language * weights.get("language", 0.0) +
            behavior * weights.get("behavior", 0.0)
        ) / 100.0

        return NormalizationEngine.normalize(overall_score)
