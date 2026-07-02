"""
Request/response logging middleware.

Logs every incoming request and outgoing response with timing information.
Provides structured observability for debugging and monitoring.
"""

import time
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs request method, path, status code, and duration."""

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        start_time = time.perf_counter()
        request_id = f"{time.time_ns()}"

        logger.bind(request_id=request_id).info(
            "→ {method} {path}",
            method=request.method,
            path=request.url.path,
        )

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        log_method = logger.info if response.status_code < 400 else logger.warning
        log_method(
            "← {method} {path} | {status} | {duration:.1f}ms",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.1f}"

        return response
