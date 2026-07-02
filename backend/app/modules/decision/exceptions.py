class DecisionError(Exception):
    """Base exception for the Decision module."""
    pass

class RankingCacheEmptyError(DecisionError):
    """Raised when ranking profiles are not found for decision processing."""
    pass

class DecisionEngineError(DecisionError):
    """Raised when the decision engine fails to process candidate profiles."""
    pass
