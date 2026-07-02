"""
JSON Exporter for the complete AI output export.

Serializes the full per‑candidate intelligence payload including:
    - Overall and component scores
    - Decision / recommendation
    - Confidence estimate
    - Reason codes
    - Feature scores (all 7 dimensions)
    - Semantic similarity score
    - Raw metadata diagnostics

Output format is a JSON object with top-level keys:
    {
        "generated_at": "...",
        "profile": "...",
        "candidate_count": N,
        "candidates": [ {...}, ... ]
    }
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.modules.export.utils import compute_checksum


class JSONExporter:
    """Serializes full AI output to JSON for complete intelligence export."""

    @staticmethod
    def export(
        candidates: List[Dict[str, Any]],
        profile: str,
        generated_at: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Build the complete JSON export string.

        Parameters
        ----------
        candidates:
            Validated, rank-annotated candidate dicts.
        profile:
            The weight profile name used to produce these rankings.
        generated_at:
            Optional timestamp string. If not provided, current UTC time is used.

        Returns
        -------
        tuple[str, str]
            (json_content, sha256_checksum)
        """
        payload: Dict[str, Any] = {
            "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
            "profile": profile,
            "candidate_count": len(candidates),
            "candidates": [
                {
                    "rank": c["rank"],
                    "candidate_id": c["candidate_id"],
                    "name": c["name"],
                    "title": c["title"],
                    "scores": {
                        "overall": c["overall_score"],
                        "semantic": c["semantic_score"],
                        "skill": c["skill_score"],
                        "experience": c["experience_score"],
                        "education": c["education_score"],
                        "certification": c["certification_score"],
                        "language": c["language_score"],
                        "behavior": c["behavior_score"],
                    },
                    "decision": {
                        "label": c.get("decision"),
                        "confidence": c.get("confidence"),
                        "recommendation": c.get("recommendation"),
                        "reason_codes": c.get("reason_codes", []),
                    },
                    "metadata": c.get("metadata", {}),
                }
                for c in candidates
            ],
        }

        json_content = json.dumps(payload, ensure_ascii=False, indent=2)
        checksum = compute_checksum(json_content)
        return json_content, checksum

    @staticmethod
    def filename(limit: int, profile: str) -> str:
        """Return the canonical JSON export filename."""
        return f"aura_ai_output_top{limit}_{profile}.json"
