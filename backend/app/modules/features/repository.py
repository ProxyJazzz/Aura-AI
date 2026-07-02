import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from loguru import logger

from app.shared.database import get_db_connection
from app.modules.features.models import CREATE_FEATURE_PROFILES_TABLE


class FeatureRepository:
    """Repository responsible for persisting candidate feature profile scorecards in SQLite."""

    @staticmethod
    def create_tables():
        """Create the features cache tables if they do not exist."""
        with get_db_connection() as conn:
            conn.execute(CREATE_FEATURE_PROFILES_TABLE)
            logger.info("Features cache tables initialized successfully.")

    @staticmethod
    def save_feature_profile(profile: Dict[str, Any]) -> None:
        """Save a single feature profile scorecard to the database."""
        FeatureRepository.create_tables()
        created_at = datetime.now(timezone.utc).isoformat()
        
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO feature_profiles (
                    candidate_id, semantic_score, skill_score, experience_score,
                    education_score, certification_score, language_score, behavior_score,
                    feature_vector, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    profile["candidate_id"],
                    profile["semantic_score"],
                    profile["skill_score"],
                    profile["experience_score"],
                    profile["education_score"],
                    profile["certification_score"],
                    profile["language_score"],
                    profile["behavior_score"],
                    json.dumps(profile["feature_vector"]),
                    json.dumps(profile["metadata"]),
                    created_at
                )
            )

    @staticmethod
    def save_feature_profiles_batch(profiles: List[Dict[str, Any]]) -> None:
        """Batch save multiple candidate feature profile scorecards to the database."""
        FeatureRepository.create_tables()
        if not profiles:
            return
        created_at = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO feature_profiles (
                    candidate_id, semantic_score, skill_score, experience_score,
                    education_score, certification_score, language_score, behavior_score,
                    feature_vector, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                [
                    (
                        p["candidate_id"],
                        p["semantic_score"],
                        p["skill_score"],
                        p["experience_score"],
                        p["education_score"],
                        p["certification_score"],
                        p["language_score"],
                        p["behavior_score"],
                        json.dumps(p["feature_vector"]),
                        json.dumps(p["metadata"]),
                        created_at
                    )
                    for p in profiles
                ]
            )

    @staticmethod
    def get_feature_profile(candidate_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single candidate's feature scorecard from SQLite."""
        FeatureRepository.create_tables()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT candidate_id, semantic_score, skill_score, experience_score,
                       education_score, certification_score, language_score, behavior_score,
                       feature_vector, metadata
                FROM feature_profiles WHERE candidate_id = ? LIMIT 1;
                """,
                (candidate_id,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "candidate_id": row[0],
                    "semantic_score": row[1],
                    "skill_score": row[2],
                    "experience_score": row[3],
                    "education_score": row[4],
                    "certification_score": row[5],
                    "language_score": row[6],
                    "behavior_score": row[7],
                    "feature_vector": json.loads(row[8]),
                    "metadata": json.loads(row[9])
                }
            return None

    @staticmethod
    def get_all_feature_profiles() -> Dict[str, Dict[str, Any]]:
        """Retrieve all cached candidate feature scorecards from SQLite."""
        FeatureRepository.create_tables()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT candidate_id, semantic_score, skill_score, experience_score,
                       education_score, certification_score, language_score, behavior_score,
                       feature_vector, metadata
                FROM feature_profiles;
                """
            )
            rows = cursor.fetchall()
            profiles = {}
            for row in rows:
                profiles[row[0]] = {
                    "candidate_id": row[0],
                    "semantic_score": row[1],
                    "skill_score": row[2],
                    "experience_score": row[3],
                    "education_score": row[4],
                    "certification_score": row[5],
                    "language_score": row[6],
                    "behavior_score": row[7],
                    "feature_vector": json.loads(row[8]),
                    "metadata": json.loads(row[9])
                }
            return profiles

    @staticmethod
    def clear_feature_profiles() -> None:
        """Clear all stored candidate feature profiles from SQLite."""
        FeatureRepository.create_tables()
        with get_db_connection() as conn:
            conn.execute("DELETE FROM feature_profiles;")
