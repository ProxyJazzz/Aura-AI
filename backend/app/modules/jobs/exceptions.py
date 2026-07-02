class JobException(Exception):
    """Base exception for all Recruiter Intelligence Module errors."""
    pass

class JobNotFoundError(JobException):
    """Raised when the requested job description or active profile is not found."""
    pass

class FileValidationError(JobException):
    """Raised when an uploaded file fails validation checks (size, type, corrupt)."""
    pass

class ParsingError(JobException):
    """Raised when parsing the uploaded document text fails."""
    pass
