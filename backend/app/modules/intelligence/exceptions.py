class IntelligenceError(Exception):
    """Base exception for the Intelligence module."""
    pass

class CandidateNotFoundError(IntelligenceError):
    """Raised when a candidate required for comparison is not found."""
    pass

class InsufficientDataError(IntelligenceError):
    """Raised when there is not enough data to generate insights or aggregates."""
    pass
