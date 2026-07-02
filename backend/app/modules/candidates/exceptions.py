class CandidateException(Exception):
    """Base exception for all Candidate Intelligence Layer errors."""
    pass

class CandidateNotFoundError(CandidateException):
    """Raised when a requested candidate is not found in the database."""
    pass

class ParseError(CandidateException):
    """Raised when streaming or parsing candidates dataset files fail."""
    pass

class ValidationError(CandidateException):
    """Raised when candidate record fails schema validation checks."""
    pass
