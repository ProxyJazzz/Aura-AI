import time
from contextlib import contextmanager
from typing import Dict, Any, Generator
from loguru import logger

class FeatureBenchmark:
    """Utility class to measure execution latency, throughput, and performance metrics."""

    @staticmethod
    @contextmanager
    def time_operation(name: str) -> Generator[Dict[str, Any], None, None]:
        """Context manager to profile execution durations."""
        metrics = {"start": time.perf_counter(), "elapsed_ms": 0.0}
        yield metrics
        metrics["elapsed_ms"] = (time.perf_counter() - metrics["start"]) * 1000.0
        logger.info("Performance Profiler: Feature Intelligence operation '{name}' took {duration:.2f}ms", 
                    name=name, duration=metrics["elapsed_ms"])

    @staticmethod
    def calculate_throughput(total_items: int, duration_ms: float) -> float:
        """Calculate processing throughput in items per second."""
        if duration_ms <= 0.0:
            return 0.0
        seconds = duration_ms / 1000.0
        return round(total_items / seconds, 2)
