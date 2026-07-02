import os
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
import numpy as np
from loguru import logger

from app.modules.semantic.cache_service import CacheService
from app.modules.semantic.repository import SemanticRepository


class EmbeddingCache:
    """Coordinates disk, memory, and database caching for Candidate and Job vector embeddings."""

    # In-memory singletons for fast retrieval
    _cached_matrix: Optional[np.ndarray] = None
    _cached_ids: Optional[List[str]] = None

    _active_job_id: Optional[str] = None
    _active_job_embedding: Optional[np.ndarray] = None

    @classmethod
    def load_candidate_cache(cls, force: bool = False) -> Tuple[np.ndarray, List[str]]:
        """Load candidate embeddings into RAM."""
        if force or cls._cached_matrix is None or cls._cached_ids is None:
            matrix, ids = CacheService.load_cache()
            cls._cached_matrix = matrix
            cls._cached_ids = ids
        return cls._cached_matrix, cls._cached_ids

    @classmethod
    def save_candidate_cache(cls, embeddings: np.ndarray, candidate_ids: List[str]) -> None:
        """Persist candidate vectors to disk cache files and syncs memory."""
        CacheService.save_cache(embeddings, candidate_ids)
        cls._cached_matrix = embeddings
        cls._cached_ids = candidate_ids

    @classmethod
    def get_job_embedding(cls, job_id: str) -> Optional[np.ndarray]:
        """Fetch the active job vector embedding from memory cache or SQLite."""
        if cls._active_job_id == job_id and cls._active_job_embedding is not None:
            return cls._active_job_embedding

        # Fallback to DB repository
        embedding = SemanticRepository.get_job_embedding(job_id)
        if embedding is not None:
            cls._active_job_id = job_id
            cls._active_job_embedding = embedding
            return embedding
        return None

    @classmethod
    def save_job_embedding(cls, job_id: str, embedding: np.ndarray) -> None:
        """Cache the active job vector embedding in memory and persists it to SQLite."""
        cls._active_job_id = job_id
        cls._active_job_embedding = embedding
        SemanticRepository.save_job_embedding(job_id, embedding)

    @classmethod
    def get_semantic_matches(cls, job_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch cached semantic similarity matches from SQLite."""
        return SemanticRepository.get_semantic_matches(job_id, limit)

    @classmethod
    def save_semantic_matches(cls, job_id: str, matches: List[Dict[str, Any]]) -> None:
        """Persist computed similarity scores for a job profile to SQLite."""
        SemanticRepository.save_semantic_matches(job_id, matches)

    @classmethod
    def delete_job_cache(cls, job_id: str) -> None:
        """Delete cached details for a job description from database and memory."""
        if cls._active_job_id == job_id:
            cls._active_job_id = None
            cls._active_job_embedding = None
        SemanticRepository.delete_job_embedding(job_id)

    @classmethod
    def clear(cls) -> None:
        """Clear memory matrices and disk cache files."""
        cls._cached_matrix = None
        cls._cached_ids = None
        cls._active_job_id = None
        cls._active_job_embedding = None
        CacheService.clear_cache()
        
        # Ensure cache tables exist
        SemanticRepository.create_tables()
        
        # Simple truncate of DB tables
        from app.shared.database import get_db_connection
        with get_db_connection() as conn:
            conn.execute("DELETE FROM semantic_job_embeddings;")
            conn.execute("DELETE FROM semantic_matches;")

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Compile status statistics."""
        status_data = CacheService.get_cache_status()
        status_data["has_active_job_vector"] = cls._active_job_embedding is not None
        status_data["active_job_id"] = cls._active_job_id
        return status_data
