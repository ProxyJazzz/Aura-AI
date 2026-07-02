from typing import List
from app.modules.ranking.configuration import RankingEntry

class RankingEngine:
    """Sorts candidates with tie-breaker logic."""

    @classmethod
    def rank(cls, candidates: List[RankingEntry]) -> List[RankingEntry]:
        """
        Deterministic sorting.
        1. overall_score (desc)
        2. semantic_score (desc)
        3. skill_score (desc)
        4. experience_score (desc)
        5. candidate_id (asc)
        """
        candidates.sort(key=lambda x: (
            -x.overall_score,
            -x.semantic_score,
            -x.skill_score,
            -x.experience_score,
            x.candidate_id
        ))
        return candidates
