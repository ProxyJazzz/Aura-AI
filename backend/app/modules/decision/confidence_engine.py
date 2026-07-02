import math
from app.modules.decision.decision_profile import DecisionProfile

class ConfidenceEngine:
    """Computes mathematically derived confidence combining ranking confidence and feature consistency."""

    @classmethod
    def evaluate(cls, profile: DecisionProfile):
        """
        Confidence formula:
        Base: Normalized overall score (score / 100).
        Penalty: High variance across feature dimensions reduces confidence.
        """
        base = profile.overall_score / 100.0
        
        # Calculate standard deviation of feature scores
        features = [
            profile.semantic_score,
            profile.skill_score,
            profile.experience_score,
            profile.education_score,
            profile.certification_score,
            profile.language_score,
            profile.behavior_score
        ]
        
        mean = sum(features) / len(features)
        variance = sum((f - mean) ** 2 for f in features) / len(features)
        std_dev = math.sqrt(variance)
        
        # Max standard deviation could theoretically be ~50 (if some are 0 and some are 100)
        # Normalize penalty so a std_dev of 50 subtracts 0.20 max
        penalty = (std_dev / 50.0) * 0.20
        
        confidence = base - penalty
        profile.confidence = min(1.0, max(0.0, round(confidence, 2)))
