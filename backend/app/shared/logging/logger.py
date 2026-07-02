"""
Structured logging configuration using Loguru.

Replaces the standard logging module with structured, colored, rotated logs.
Configures both console output (human-readable) and file output (JSON).
"""

import sys
from loguru import logger

from app.shared.config.settings import settings


def setup_logging() -> None:
    """Configure Loguru for the application."""

    # Remove default handler
    logger.remove()

    # Console handler — human-readable with colors
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=settings.is_development,
    )

    # File handler — JSON-structured for log aggregation
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="gz",
        serialize=settings.LOG_FORMAT == "json",
        backtrace=True,
        diagnose=False,
    )

    logger.info(
        "Logging initialized | level={level} | env={env}",
        level=settings.LOG_LEVEL,
        env=settings.APP_ENV,
    )
