class FeatureException(Exception):
    """Base exception for all Feature Intelligence Layer errors."""
    pass

class FeatureCacheNotBuiltError(FeatureException):
    """Raised when queries are made to candidates features but the cache file is missing."""
    pass

class FeatureActiveJobNotFoundError(FeatureException):
    """Raised when cache builds or scoring are requested but no active job description is set."""
    pass

class FeatureServiceIntegrationError(FeatureException):
    """Raised when calls to Candidate, Job, or Semantic services fail."""
    pass
