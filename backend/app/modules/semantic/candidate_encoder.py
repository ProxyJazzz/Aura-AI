from typing import List, Dict, Any
import numpy as np
from app.modules.semantic.embedding_manager import EmbeddingManager
from app.modules.semantic.utils import format_candidate_text


class CandidateEncoder:
    """Encodes Candidate Profiles into vector embeddings using EmbeddingManager."""

    @classmethod
    def encode_candidates(cls, candidates: List[Dict[str, Any]], batch_size: int = 256) -> np.ndarray:
        """Format candidate dictionary entries and build vector embeddings in batch."""
        if not candidates:
            return np.empty((0, 384), dtype=np.float32)
        texts = [format_candidate_text(c) for c in candidates]
        return EmbeddingManager.generate_embeddings(texts, batch_size=batch_size)
