"""
Custom exception definitions for the Export / Submission Engine module.

Hierarchy:
    ExportError
    ├── ValidationError
    ├── ExportCacheError
    └── ExportServiceIntegrationError
"""


class ExportError(Exception):
    """Base exception for all export‑related errors."""
    pass


class ValidationError(ExportError):
    """Raised when pre‑export validation fails."""

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class ExportCacheError(ExportError):
    """Raised when the export SQLite cache cannot be read or written."""
    pass


class ExportServiceIntegrationError(ExportError):
    """Raised when upstream service calls (Ranking, Candidate, Job, Analytics) fail."""
    pass
