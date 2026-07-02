class SemanticException(Exception):
    """Base exception for all Semantic Intelligence Layer errors."""
    pass

class CacheNotBuiltError(SemanticException):
    """Raised when similarity search is requested but candidate embeddings cache is missing."""
    pass

class ActiveJobNotFoundError(SemanticException):
    """Raised when job embedding generation is requested but no job description is active."""
    pass

class ServiceIntegrationError(SemanticException):
    """Raised when calls to CandidateService or JobService fail or return invalid data."""
    pass

class ModelLoadError(SemanticException):
    """Raised when SentenceTransformer fails to load or configure its execution device."""
    pass
