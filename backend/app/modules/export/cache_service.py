"""
SQLite-backed cache for the Export / Submission Engine.

Tables
------
export_artifacts
    Stores generated file blobs (CSV / JSON / report JSON), metadata, and
    the SHA-256 checksum of each artifact.

export_history
    Append-only log of every export event with timing and user context.

Design notes
------------
- One SQLite file per backend instance (export_cache.db alongside the app).
- Thread-safe: each call obtains its own connection.
- Profile-keyed: every row carries a `profile` column so multiple ranking
  profiles can coexist in the cache without conflicts.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


# ── Path resolution ───────────────────────────────────────────────────────────


def _db_path() -> Path:
    """Resolve path to export_cache.db (sits next to the backend/ directory)."""
    return Path(__file__).resolve().parent.parent.parent.parent / "export_cache.db"


# ── Connection helper ─────────────────────────────────────────────────────────


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


# ── Schema bootstrap ──────────────────────────────────────────────────────────


def _bootstrap() -> None:
    """Create tables if they do not already exist."""
    with _get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS export_artifacts (
                export_id    TEXT PRIMARY KEY,
                export_type  TEXT NOT NULL,
                profile      TEXT NOT NULL,
                candidate_count INTEGER NOT NULL,
                checksum     TEXT NOT NULL,
                filename     TEXT NOT NULL,
                blob         BLOB NOT NULL,
                created_at   TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_export_type
                ON export_artifacts(export_type);
            CREATE INDEX IF NOT EXISTS idx_export_profile
                ON export_artifacts(profile);

            CREATE TABLE IF NOT EXISTS export_history (
                history_id   TEXT PRIMARY KEY,
                export_id    TEXT NOT NULL,
                export_type  TEXT NOT NULL,
                profile      TEXT,
                user_id      TEXT,
                candidate_count INTEGER NOT NULL,
                duration_ms  INTEGER NOT NULL,
                checksum     TEXT NOT NULL,
                created_at   TEXT NOT NULL,
                FOREIGN KEY (export_id) REFERENCES export_artifacts(export_id)
            );
            """
        )


# ── Public API ────────────────────────────────────────────────────────────────


class ExportCacheService:
    """Manages SQLite persistence of generated export artifacts and history."""

    @staticmethod
    def store_export(
        *,
        export_type: str,
        profile: str,
        blob: bytes,
        filename: str,
        checksum: str,
        candidate_count: int,
        duration_ms: int,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Persist an export artifact and append a history row.

        Returns
        -------
        str
            The newly generated export_id (UUID4).
        """
        _bootstrap()
        export_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        with _get_conn() as conn:
            conn.execute(
                """
                INSERT INTO export_artifacts
                    (export_id, export_type, profile, candidate_count,
                     checksum, filename, blob, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    export_id,
                    export_type,
                    profile,
                    candidate_count,
                    checksum,
                    filename,
                    blob,
                    now,
                ),
            )

            history_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO export_history
                    (history_id, export_id, export_type, profile, user_id,
                     candidate_count, duration_ms, checksum, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    history_id,
                    export_id,
                    export_type,
                    profile,
                    user_id,
                    candidate_count,
                    duration_ms,
                    checksum,
                    now,
                ),
            )

        logger.info(
            "Stored export artifact: id={export_id} type={export_type} "
            "candidates={n} profile={profile}",
            export_id=export_id,
            export_type=export_type,
            n=candidate_count,
            profile=profile,
        )
        return export_id

    @staticmethod
    def fetch_export(export_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single export artifact row by its ID."""
        _bootstrap()
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM export_artifacts WHERE export_id = ?",
                (export_id,),
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def list_history(limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent *limit* export history entries (newest first)."""
        _bootstrap()
        with _get_conn() as conn:
            rows = conn.execute(
                """
                SELECT history_id, export_id, export_type, profile, user_id,
                       candidate_count, duration_ms, checksum, created_at
                FROM export_history
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Return high-level cache statistics."""
        _bootstrap()
        with _get_conn() as conn:
            total = conn.execute(
                "SELECT COUNT(*) AS cnt FROM export_history"
            ).fetchone()["cnt"]

            latest = conn.execute(
                """
                SELECT export_type, created_at, candidate_count, checksum
                FROM export_history
                ORDER BY created_at DESC
                LIMIT 1
                """
            ).fetchone()

        status: Dict[str, Any] = {"total_exports": total}
        if latest:
            status.update(
                {
                    "last_export_type": latest["export_type"],
                    "last_export_at": latest["created_at"],
                    "last_export_candidate_count": latest["candidate_count"],
                    "last_checksum": latest["checksum"],
                }
            )
        return status

    @staticmethod
    def clear_cache(profile: Optional[str] = None) -> None:
        """Delete export artifacts (and their history rows) for a profile or all."""
        _bootstrap()
        with _get_conn() as conn:
            if profile:
                ids = [
                    row[0]
                    for row in conn.execute(
                        "SELECT export_id FROM export_artifacts WHERE profile = ?",
                        (profile,),
                    ).fetchall()
                ]
                conn.execute(
                    "DELETE FROM export_history WHERE export_id IN "
                    f"({','.join('?' * len(ids))})",
                    ids,
                )
                conn.execute(
                    "DELETE FROM export_artifacts WHERE profile = ?", (profile,)
                )
            else:
                conn.execute("DELETE FROM export_history")
                conn.execute("DELETE FROM export_artifacts")
        logger.info("Export cache cleared. profile={profile}", profile=profile or "ALL")
