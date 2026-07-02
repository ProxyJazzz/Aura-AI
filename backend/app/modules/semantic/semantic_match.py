from typing import Dict, Any


class SemanticMatch:
    """Represents a structured semantic match object between a candidate and a job description."""

    def __init__(self, candidate_id: str, score: float):
        self.candidate_id = candidate_id
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "score": self.score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticMatch":
        return cls(candidate_id=data["candidate_id"], score=data["score"])
