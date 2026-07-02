import time
from typing import Callable, Any, Tuple
from loguru import logger


def normalize_score(score: float) -> float:
    """Clips score to [0.0, 100.0] range."""
    return float(max(0.0, min(100.0, score)))


def time_scoring_operation(
    engine_name: str,
    func: Callable[..., Tuple[float, Dict[str, Any]]],
    *args,
    **kwargs
) -> Tuple[float, Dict[str, Any]]:
    """Times execution duration of feature scoring calculations."""
    start_time = time.perf_counter()
    try:
        score, metadata = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metadata["elapsed_ms"] = round(elapsed_ms, 3)
        return normalize_score(score), metadata
    except Exception as e:
        logger.exception("{name} calculation failed: {err}", name=engine_name, err=str(e))
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return 0.0, {
            "error": f"Scoring error: {str(e)}",
            "elapsed_ms": round(elapsed_ms, 3)
        }
