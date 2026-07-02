from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class DecisionProfile:
    """Internal data structure for Decision computations."""
    candidate_id: str
    profile: str
    rank: int
    overall_score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    education_score: float
    certification_score: float
    language_score: float
    behavior_score: float
    
    recommendation: str = ""
    confidence: float = 0.0
    risk_level: str = "Low"
    reason_codes: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    next_action: str = ""
    
    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "profile": self.profile,
            "rank": self.rank,
            "overall_score": self.overall_score,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "reason_codes": ",".join(self.reason_codes),
            "strengths": ",".join(self.strengths),
            "gaps": ",".join(self.gaps),
            "next_action": self.next_action
        }
