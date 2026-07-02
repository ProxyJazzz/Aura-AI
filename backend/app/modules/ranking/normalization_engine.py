class NormalizationEngine:
    """Clamps candidate scores to [0, 100]."""

    @classmethod
    def normalize(cls, score: float) -> float:
        """Clamps the score to a maximum of 100 and minimum of 0."""
        return min(100.0, max(0.0, round(float(score), 2)))
