"""
Utility helpers for the Export / Submission Engine module.

Responsibilities:
    - SHA-256 checksum generation for deterministic submission fingerprints.
    - Deterministic ranking tie-breaker (mirrors the Ranking engine's logic).
    - Profile name resolution (fall back to system default when None).
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional


# ── Constants ─────────────────────────────────────────────────────────────────

AURA_VERSION = "1.0.0"
DEFAULT_PROFILE = "default"

# Canonical CSV column order (Hack2Skill submission format)
CSV_COLUMNS = [
    "rank",
    "candidate_id",
    "name",
    "title",
    "overall_score",
    "semantic_score",
    "skill_score",
    "experience_score",
    "education_score",
    "certification_score",
    "language_score",
    "behavior_score",
    "decision",
    "confidence",
    "recommendation",
]


# ── Checksum ──────────────────────────────────────────────────────────────────


def compute_checksum(data: str | bytes) -> str:
    """Return the SHA-256 hex digest of *data* (string or bytes)."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


# ── Profile Resolution ────────────────────────────────────────────────────────


def resolve_profile(profile: Optional[str]) -> str:
    """Return *profile* if given, otherwise return the system default name."""
    return profile.strip() if profile else DEFAULT_PROFILE


# ── Tie-breaker Sort ──────────────────────────────────────────────────────────


def deterministic_sort(
    candidates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Sort candidates deterministically by:
      1. overall_score      (desc)
      2. semantic_score     (desc)
      3. skill_score        (desc)
      4. experience_score   (desc)
      5. candidate_id       (asc  — string tie-breaker for reproducibility)
    """
    return sorted(
        candidates,
        key=lambda c: (
            -c.get("overall_score", 0.0),
            -c.get("semantic_score", 0.0),
            -c.get("skill_score", 0.0),
            -c.get("experience_score", 0.0),
            c.get("candidate_id", ""),
        ),
    )


# ── Limit Resolution ─────────────────────────────────────────────────────────


def resolve_limit(limit: Optional[int], default: int = 10) -> int:
    """Return the caller-supplied *limit* or *default* when None."""
    return limit if limit is not None else default
