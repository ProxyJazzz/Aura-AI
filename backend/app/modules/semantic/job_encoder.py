from typing import Dict, Any
import numpy as np
from app.modules.semantic.embedding_manager import EmbeddingManager
from app.modules.semantic.utils import format_job_text


class JobEncoder:
    """Encodes structured Hiring Profile objects into vector embeddings."""

    @classmethod
    def encode_job(cls, job: Dict[str, Any]) -> np.ndarray:
        """Format the job object and generate a single active vector embedding."""
        text = format_job_text(job)
        embeddings = EmbeddingManager.generate_embeddings([text], batch_size=1)
        return embeddings[0]
