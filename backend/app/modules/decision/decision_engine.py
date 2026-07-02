from app.modules.decision.decision_profile import DecisionProfile
from app.modules.decision.recommendation_engine import RecommendationEngine
from app.modules.decision.confidence_engine import ConfidenceEngine
from app.modules.decision.risk_engine import RiskEngine
from app.modules.decision.reason_engine import ReasonEngine

class DecisionEngine:
    """Unifies Recommendation, Confidence, Risk, and Reason engines."""

    @classmethod
    def evaluate_profile(cls, profile: DecisionProfile) -> DecisionProfile:
        """Pipes a single DecisionProfile through all evaluation engines."""
        RecommendationEngine.evaluate(profile)
        ConfidenceEngine.evaluate(profile)
        RiskEngine.evaluate(profile)
        ReasonEngine.evaluate(profile)
        return profile
