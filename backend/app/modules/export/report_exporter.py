"""
Recruiter Report Exporter.

Generates a structured recruiter‑readable JSON report containing:
    - Job summary (title, required/preferred skills, seniority, industry)
    - Top candidates (rank, scores, decision, recommendation)
    - Analytics summary (score distribution, average scores per dimension)
    - Recommendation summary (counts per decision label)
    - Hiring statistics (total evaluated, acceptance rate, mean confidence)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.modules.export.utils import compute_checksum


class ReportExporter:
    """Generates recruiter‑facing intelligence report in JSON format."""

    @staticmethod
    def _score_distribution(scores: List[float]) -> Dict[str, int]:
        """Bucket overall scores into ranges for analytics."""
        buckets = {"90-100": 0, "75-89": 0, "60-74": 0, "40-59": 0, "0-39": 0}
        for s in scores:
            if s >= 90:
                buckets["90-100"] += 1
            elif s >= 75:
                buckets["75-89"] += 1
            elif s >= 60:
                buckets["60-74"] += 1
            elif s >= 40:
                buckets["40-59"] += 1
            else:
                buckets["0-39"] += 1
        return buckets

    @staticmethod
    def _avg(values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)

    @classmethod
    def export(
        cls,
        candidates: List[Dict[str, Any]],
        active_job: Optional[Dict[str, Any]],
        profile: str,
    ) -> tuple[str, str]:
        """
        Build the recruiter intelligence report JSON.

        Parameters
        ----------
        candidates:
            Validated, ranked candidate records.
        active_job:
            Dict from JobService.get_active_job() (may be None if none uploaded).
        profile:
            Weight profile name.

        Returns
        -------
        tuple[str, str]
            (json_content, sha256_checksum)
        """
        # ── Job summary ───────────────────────────────────────────────────────
        job_summary: Dict[str, Any] = {}
        if active_job:
            job_summary = {
                "id": active_job.get("id"),
                "title": active_job.get("title"),
                "seniority": active_job.get("seniority"),
                "employment_type": active_job.get("employment_type"),
                "industry": active_job.get("industry"),
                "required_skills": active_job.get("required_skills", []),
                "preferred_skills": active_job.get("preferred_skills", []),
                "min_experience_years": active_job.get("min_experience"),
            }

        # ── Analytics ─────────────────────────────────────────────────────────
        all_scores = [c["overall_score"] for c in candidates]
        analytics = {
            "total_evaluated": len(candidates),
            "score_distribution": cls._score_distribution(all_scores),
            "average_scores": {
                "overall": cls._avg(all_scores),
                "semantic": cls._avg([c["semantic_score"] for c in candidates]),
                "skill": cls._avg([c["skill_score"] for c in candidates]),
                "experience": cls._avg([c["experience_score"] for c in candidates]),
                "education": cls._avg([c["education_score"] for c in candidates]),
                "certification": cls._avg([c["certification_score"] for c in candidates]),
                "language": cls._avg([c["language_score"] for c in candidates]),
                "behavior": cls._avg([c["behavior_score"] for c in candidates]),
            },
        }

        # ── Recommendation summary ────────────────────────────────────────────
        rec_counts: Dict[str, int] = {}
        for c in candidates:
            label = c.get("decision") or "UNKNOWN"
            rec_counts[label] = rec_counts.get(label, 0) + 1

        confidences = [c["confidence"] for c in candidates if c.get("confidence") is not None]
        hiring_stats = {
            "total_candidates_ranked": len(candidates),
            "mean_confidence": cls._avg(confidences) if confidences else None,
            "top_score": max(all_scores) if all_scores else None,
            "bottom_score": min(all_scores) if all_scores else None,
        }

        # ── Assemble report ───────────────────────────────────────────────────
        report: Dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "profile": profile,
            "job_summary": job_summary,
            "top_candidates": [
                {
                    "rank": c["rank"],
                    "candidate_id": c["candidate_id"],
                    "name": c["name"],
                    "title": c["title"],
                    "overall_score": c["overall_score"],
                    "decision": c.get("decision"),
                    "confidence": c.get("confidence"),
                    "recommendation": c.get("recommendation"),
                }
                for c in candidates[:25]  # top 25 for report
            ],
            "analytics": analytics,
            "recommendation_summary": rec_counts,
            "hiring_statistics": hiring_stats,
        }

        json_content = json.dumps(report, ensure_ascii=False, indent=2)
        checksum = compute_checksum(json_content)
        return json_content, checksum

    @staticmethod
    def filename(profile: str) -> str:
        """Return the canonical report filename."""
        return f"aura_recruiter_report_{profile}.json"
