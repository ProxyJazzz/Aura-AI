"""
Global exception handlers registered on the FastAPI application.

Converts all exceptions into consistent JSON error responses.
Ensures no unhandled exceptions leak stack traces in production.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.shared.exceptions.errors import AuraBaseError


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(AuraBaseError)
    async def aura_error_handler(request: Request, exc: AuraBaseError) -> JSONResponse:
        """Handle all application-specific errors."""
        logger.warning(
            "Application error | code={code} | status={status} | path={path} | message={message}",
            code=exc.error_code,
            status=exc.status_code,
            path=request.url.path,
            message=exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic/FastAPI request validation errors."""
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": " → ".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        logger.warning(
            "Validation error | path={path} | errors={count}",
            path=request.url.path,
            count=len(errors),
        )
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed.",
                    "details": {"errors": errors},
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for unhandled exceptions. Logs full traceback, returns generic error."""
        logger.exception(
            "Unhandled exception | path={path} | type={type}",
            path=request.url.path,
            type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                    "details": {},
                },
            },
        )
