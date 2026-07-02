from typing import Tuple

class ConfidenceEngine:
    """Evaluates candidate data completeness and computes reliability scores."""

    @classmethod
    def evaluate(cls, overall_score: float) -> Tuple[str, float, str]:
        """
        Mock Decision Intelligence logic.
        Returns: decision, confidence, recommendation
        """
        if overall_score >= 85:
            decision = "STRONG_YES"
            confidence = round(0.85 + (overall_score - 85) * 0.01, 2)
            recommendation = "Highly qualified candidate. Recommend immediate interview."
        elif overall_score >= 70:
            decision = "YES"
            confidence = round(0.70 + (overall_score - 70) * 0.01, 2)
            recommendation = "Qualified candidate. Proceed to screening."
        elif overall_score >= 50:
            decision = "MAYBE"
            confidence = round(0.60 + (overall_score - 50) * 0.005, 2)
            recommendation = "Potential match. Keep in talent pool."
        else:
            decision = "NO"
            confidence = round(0.80 - overall_score * 0.005, 2)
            recommendation = "Low fit alignment. Reconsider."
            
        return decision, min(1.0, max(0.0, confidence)), recommendation
