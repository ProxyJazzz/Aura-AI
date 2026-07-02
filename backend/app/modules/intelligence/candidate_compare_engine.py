from typing import Dict, Any
from app.modules.intelligence.schema import CandidateCompareData, CandidateComparisonResponse
from app.modules.intelligence.exceptions import CandidateNotFoundError

class CandidateCompareEngine:
    """Compares two candidate decision profiles deterministically."""

    @classmethod
    def evaluate(cls, d1: Dict[str, Any], d2: Dict[str, Any]) -> CandidateComparisonResponse:
        
        def _map_to_data(d: Dict[str, Any]) -> CandidateCompareData:
            return CandidateCompareData(
                candidate_id=d["candidate_id"],
                semantic_score=d.get("semantic_score", 0),
                skill_score=d.get("skill_score", 0),
                experience_score=d.get("experience_score", 0),
                education_score=d.get("education_score", 0),
                overall_score=d.get("overall_score", 0),
                confidence=d.get("confidence", 0),
                recommendation=d.get("recommendation", "Unknown"),
                risk_level=d.get("risk_level", "Unknown")
            )

        c1 = _map_to_data(d1)
        c2 = _map_to_data(d2)

        winner = c1.candidate_id if c1.overall_score >= c2.overall_score else c2.candidate_id
        delta = abs(c1.overall_score - c2.overall_score)

        return CandidateComparisonResponse(
            candidate1=c1,
            candidate2=c2,
            winner=winner,
            delta_score=round(delta, 2)
        )
