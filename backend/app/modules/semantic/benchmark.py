import time
from contextlib import contextmanager
from typing import Dict, Any, Generator
from loguru import logger

class Benchmark:
    """Utility class to measure execution durations and log performance metrics."""

    @staticmethod
    @contextmanager
    def time_operation(name: str) -> Generator[Dict[str, Any], None, None]:
        """
        Context manager that yields a dictionary containing timing metrics.
        Logs the elapsed time on context exit.
        """
        metrics = {"start": time.perf_counter(), "elapsed_ms": 0.0}
        yield metrics
        metrics["elapsed_ms"] = (time.perf_counter() - metrics["start"]) * 1000.0
        logger.info("Performance Profiler: Operation '{name}' completed in {duration:.2f}ms", 
                    name=name, duration=metrics["elapsed_ms"])
