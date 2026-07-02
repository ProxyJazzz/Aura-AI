from typing import Dict, Any


class FeatureProfileGenerator:
    """Helper class to construct standardized candidate feature scorecard profiles."""

    @staticmethod
    def construct_profile(
        candidate_id: str,
        semantic_score: float,
        skill_score: float,
        experience_score: float,
        education_score: float,
        certification_score: float,
        language_score: float,
        behavior_score: float,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        feature_vector = [
            semantic_score,
            skill_score,
            experience_score,
            education_score,
            certification_score,
            language_score,
            behavior_score
        ]
        return {
            "candidate_id": candidate_id,
            "semantic_score": round(semantic_score, 2),
            "skill_score": round(skill_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "certification_score": round(certification_score, 2),
            "language_score": round(language_score, 2),
            "behavior_score": round(behavior_score, 2),
            "feature_vector": [round(v, 2) for v in feature_vector],
            "metadata": metadata
        }
