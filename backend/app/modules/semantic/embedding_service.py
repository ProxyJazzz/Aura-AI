import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from app.modules.semantic.embedding_manager import EmbeddingManager


class EmbeddingService:
    """Singleton wrapper for legacy compatibility with EmbeddingService."""

    model_load_time_ms: float = 0.0

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        model = EmbeddingManager.get_model()
        cls.model_load_time_ms = EmbeddingManager.model_load_time_ms
        return model

    @classmethod
    def generate_embeddings(cls, texts: List[str], batch_size: int = 256) -> np.ndarray:
        res = EmbeddingManager.generate_embeddings(texts, batch_size)
        cls.model_load_time_ms = EmbeddingManager.model_load_time_ms
        return res
