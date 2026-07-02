class RankingError(Exception):
    """Base exception for ranking module."""
    pass

class InvalidWeightProfileError(RankingError):
    """Raised when a weight profile is invalid (e.g. doesn't sum to 100)."""
    pass

class FeatureCacheEmptyError(RankingError):
    """Raised when trying to rank candidates but feature cache is empty."""
    pass
