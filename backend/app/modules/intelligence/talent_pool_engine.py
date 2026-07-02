from typing import List, Dict, Any
from app.modules.intelligence.schema import DashboardIntelligence

class TalentPoolEngine:
    """Calculates overall talent pool metrics from decision data."""

    @classmethod
    def evaluate(cls, decisions: List[Dict[str, Any]]) -> DashboardIntelligence:
        total = len(decisions)
        if total == 0:
            return DashboardIntelligence(
                total_candidates=0,
                strong_hires=0,
                avg_score=0.0,
                high_risk_candidates=0
            )

        strong_hires = sum(1 for d in decisions if d.get("recommendation") == "Strong Hire")
        avg_score = sum(d.get("overall_score", 0) for d in decisions) / total
        high_risk = sum(1 for d in decisions if d.get("risk_level") == "High")

        return DashboardIntelligence(
            total_candidates=total,
            strong_hires=strong_hires,
            avg_score=round(avg_score, 2),
            high_risk_candidates=high_risk
        )
