import threading
import time
from typing import Optional, List
import os
from pathlib import Path
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from loguru import logger
from app.modules.semantic.exceptions import ModelLoadError


class EmbeddingManager:
    """Singleton wrapper for managing SentenceTransformer model instantiation thread-safely."""

    _instance: Optional[SentenceTransformer] = None
    _lock = threading.Lock()
    
    model_name: str = "all-MiniLM-L6-v2"
    model_version: str = "1.0.0"
    model_load_time_ms: float = 0.0

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Lazily initialize and return the SentenceTransformer singleton in a thread-safe manner."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    start_time = time.perf_counter()
                    logger.info("Initializing EmbeddingManager model '{model}'...", model=cls.model_name)
                    try:
                        # Smart caching: Enable offline mode dynamically ONLY if the model already exists locally.
                        # This avoids build-time downloads while also preventing offline crashes.
                        hf_home = os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface" / "hub"))
                        model_dir = Path(hf_home) / f"models--{cls.model_name.replace('/', '--')}"
                        if model_dir.exists():
                            logger.info("Local model cache detected. Enabling strict offline mode for faster startup.")
                            os.environ["TRANSFORMERS_OFFLINE"] = "1"
                            os.environ["HF_HUB_OFFLINE"] = "1"
                        else:
                            logger.warning("No local model cache detected! Downloading model now (lazy load).")
                            
                        device = "cuda" if torch.cuda.is_available() else "cpu"
                        logger.info("EmbeddingManager using device: {device}", device=device)
                        cls._instance = SentenceTransformer(cls.model_name, device=device)
                        cls.model_load_time_ms = (time.perf_counter() - start_time) * 1000.0
                        logger.info("EmbeddingManager model loaded successfully in {duration:.2f}ms.",
                                    duration=cls.model_load_time_ms)
                    except Exception as e:
                        logger.error("Failed to load embedding model: {err}", err=str(e))
                        raise ModelLoadError(f"Model load error: {str(e)}")
        return cls._instance

    @classmethod
    def generate_embeddings(cls, texts: List[str], batch_size: int = 256) -> np.ndarray:
        """Generate unit-normalized embeddings using the loaded model."""
        model = cls.get_model()
        try:
            embeddings = model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error("Error generating text embeddings: {err}", err=str(e))
            raise
