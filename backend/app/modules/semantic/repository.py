import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import numpy as np
from loguru import logger

from app.shared.database import get_db_connection
from app.modules.semantic.models import (
    CREATE_SEMANTIC_JOB_EMBEDDINGS_TABLE,
    CREATE_SEMANTIC_MATCHES_TABLE,
    CREATE_SEMANTIC_MATCHES_INDEX
)


class SemanticRepository:
    """Repository responsible for persisting vector match metrics and active job embeddings in SQLite."""

    @staticmethod
    def create_tables():
        """Create the semantic cache tables if they do not exist."""
        with get_db_connection() as conn:
            conn.execute(CREATE_SEMANTIC_JOB_EMBEDDINGS_TABLE)
            conn.execute(CREATE_SEMANTIC_MATCHES_TABLE)
            conn.execute(CREATE_SEMANTIC_MATCHES_INDEX)
            logger.info("Semantic cache tables initialized successfully.")

    @staticmethod
    def save_job_embedding(job_id: str, embedding: np.ndarray) -> None:
        """Serialize and save the active job description embedding vector."""
        SemanticRepository.create_tables()
        created_at = datetime.now(timezone.utc).isoformat()
        embedding_blob = embedding.tobytes()

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO semantic_job_embeddings (job_id, embedding, created_at)
                VALUES (?, ?, ?);
                """,
                (job_id, embedding_blob, created_at)
            )

    @staticmethod
    def get_job_embedding(job_id: str) -> Optional[np.ndarray]:
        """Retrieve the serialized active job description embedding."""
        SemanticRepository.create_tables()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT embedding FROM semantic_job_embeddings WHERE job_id = ? LIMIT 1;",
                (job_id,)
            )
            row = cursor.fetchone()
            if row:
                return np.frombuffer(row[0], dtype=np.float32)
            return None

    @staticmethod
    def save_semantic_matches(job_id: str, matches: List[Dict[str, Any]]) -> None:
        """Batch save computed semantic similarity scores for a job description."""
        SemanticRepository.create_tables()
        if not matches:
            return

        with get_db_connection() as conn:
            # Delete old matches for this job description first
            conn.execute("DELETE FROM semantic_matches WHERE job_id = ?;", (job_id,))
            
            # Batch insert new matches
            conn.executemany(
                """
                INSERT OR REPLACE INTO semantic_matches (candidate_id, job_id, score)
                VALUES (?, ?, ?);
                """,
                [(m["candidate_id"], job_id, m["score"]) for m in matches]
            )

    @staticmethod
    def get_semantic_matches(job_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve the top-K semantic match records from database cache."""
        SemanticRepository.create_tables()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT candidate_id, score FROM semantic_matches
                WHERE job_id = ?
                ORDER BY score DESC
                LIMIT ?;
                """,
                (job_id, limit)
            )
            return [{"candidate_id": row[0], "score": row[1]} for row in cursor.fetchall()]

    @staticmethod
    def delete_job_embedding(job_id: str) -> None:
        """Delete cached embedding and matches associated with a job description."""
        SemanticRepository.create_tables()
        with get_db_connection() as conn:
            conn.execute("DELETE FROM semantic_job_embeddings WHERE job_id = ?;", (job_id,))
            conn.execute("DELETE FROM semantic_matches WHERE job_id = ?;", (job_id,))
