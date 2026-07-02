import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from loguru import logger

class BaseFeatureEngine(ABC):
    """
    Abstract base class for all scoring engines in the Feature Intelligence Layer.
    Enforces standardized validation, score normalization, execution timing, and error handling.
    """

    @abstractmethod
    def _run_calculation(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculates the feature score and returns a Tuple of (raw_score, metadata).
        Must be implemented by subclasses.
        """
        pass

    def calculate(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Wraper method to run feature calculation with execution timing, error handling,
        input validation, and score clipping to [0.0, 100.0].
        """
        engine_name = self.__class__.__name__
        
        # 1. Validation
        if not candidate or not isinstance(candidate, dict):
            logger.warning("{name}: Invalid candidate payload provided.", name=engine_name)
            return 0.0, {"error": "Invalid candidate data type"}
        if not job or not isinstance(job, dict):
            logger.warning("{name}: Invalid job payload provided.", name=engine_name)
            return 0.0, {"error": "Invalid job data type"}
            
        start_time = time.perf_counter()
        try:
            # 2. Run calculations in subclass
            raw_score, metadata = self._run_calculation(candidate, job)
            
            # 3. Score Normalization & Clipping
            normalized_score = float(max(0.0, min(100.0, raw_score)))
            
            # Record timing statistics
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            metadata["elapsed_ms"] = round(elapsed_ms, 3)
            
            logger.debug("{name} computed score {score:.2f} in {duration:.3f}ms", 
                         name=engine_name, score=normalized_score, duration=elapsed_ms)
                         
            return normalized_score, metadata
            
        except Exception as e:
            logger.exception("{name} failed during calculation: {err}", name=engine_name, err=str(e))
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return 0.0, {
                "error": f"Scoring exception: {str(e)}",
                "elapsed_ms": round(elapsed_ms, 3)
            }
