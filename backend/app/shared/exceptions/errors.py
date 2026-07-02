"""
Custom exception classes for the application.

All application-specific errors inherit from AuraBaseError.
Each error carries an error code, HTTP status, and human-readable message.
"""

from typing import Any


class AuraBaseError(Exception):
    """Base exception for all AURA AI application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AuraBaseError):
    """Resource not found."""

    def __init__(
        self,
        resource: str = "Resource",
        identifier: str = "",
    ) -> None:
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} with id '{identifier}' not found"
        super().__init__(
            message=detail,
            error_code="NOT_FOUND",
            status_code=404,
        )


class ValidationError(AuraBaseError):
    """Request validation failed."""

    def __init__(
        self,
        message: str = "Validation failed.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ConflictError(AuraBaseError):
    """Resource conflict (e.g., duplicate entry)."""

    def __init__(
        self,
        message: str = "Resource already exists.",
    ) -> None:
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
        )


class UnauthorizedError(AuraBaseError):
    """Authentication required or failed."""

    def __init__(
        self,
        message: str = "Authentication required.",
    ) -> None:
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
        )


class ForbiddenError(AuraBaseError):
    """Insufficient permissions."""

    def __init__(
        self,
        message: str = "Insufficient permissions.",
    ) -> None:
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
        )


class ServiceUnavailableError(AuraBaseError):
    """Downstream service or component unavailable."""

    def __init__(
        self,
        service: str = "Service",
    ) -> None:
        super().__init__(
            message=f"{service} is temporarily unavailable.",
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
        )
