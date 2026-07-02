import numpy as np
from typing import List, Optional
from loguru import logger
import torch
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """Singleton wrapper for managing the SentenceTransformer model instance."""
    
    _model: Optional[SentenceTransformer] = None
    model_load_time_ms: float = 0.0

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Lazily load and return the SentenceTransformer model singleton."""
        if cls._model is None:
            import time
            start_time = time.perf_counter()
            logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
            try:
                # Detect CUDA GPU support, otherwise default to CPU
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info("SentenceTransformer running on device: {device}", device=device)
                
                cls._model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
                cls.model_load_time_ms = (time.perf_counter() - start_time) * 1000.0
                logger.info("SentenceTransformer model loaded successfully in {duration:.2f}ms.", 
                            duration=cls.model_load_time_ms)
            except Exception as e:
                logger.error("Failed to load SentenceTransformer model: {err}", err=str(e))
                raise RuntimeError(f"Model load error: {str(e)}")
                
        return cls._model

    @classmethod
    def generate_embeddings(cls, texts: List[str], batch_size: int = 256) -> np.ndarray:
        """
        Generate unit-normalized embeddings in batches.
        Normalizing here turns cosine similarity into a dot product.
        """
        model = cls.get_model()
        logger.info("Encoding {count} text blocks with batch size {batch}...", count=len(texts), batch=batch_size)
        try:
            embeddings = model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            # Ensure return format is float32 numpy array
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error("Error generating text embeddings: {err}", err=str(e))
            raise
