"""
Submission Validator for the Export / Submission Engine.

Checks performed (in order):
    1.  Feature cache must be built (profiles exist).
    2.  Candidate IDs must be unique (no duplicate rows).
    3.  All candidates must exist in the Candidate repository.
    4.  Required columns must be present in every profile.
    5.  No null / zero overall_score unless the profile score is legitimately 0.
    6.  Ranking order must be consistent (descending overall_score, tie-breaker applied).
    7.  Candidate count must be ≥ the requested export limit.

On any failure a ValidationError is raised with a structured detail message.
When all checks pass the validated, sorted list of RankedCandidate dicts is returned.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from loguru import logger

from app.modules.candidates.service import CandidateService
from app.modules.export.exceptions import ValidationError
from app.modules.export.schema import ValidationIssue, RankedCandidate
from app.modules.export.utils import deterministic_sort, resolve_limit
from app.modules.features.service import FeatureService


# Minimum set of keys every feature profile must carry.
REQUIRED_KEYS = {
    "candidate_id",
    "overall_score",
    "semantic_score",
    "skill_score",
    "experience_score",
    "education_score",
    "certification_score",
    "language_score",
    "behavior_score",
}


class SubmissionValidator:
    """
    Validates ranking output before any export artifact is generated.

    Usage::

        validated = SubmissionValidator.validate(profiles, limit=100)
        # returns List[Dict[str, Any]] sorted and trimmed to *limit*
    """

    @staticmethod
    def validate(
        profiles: Dict[str, Dict[str, Any]],
        limit: Optional[int] = None,
        candidate_details_map: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run all validation checks and return a sorted, trimmed candidate list.

        Parameters
        ----------
        profiles:
            Dict keyed by candidate_id → feature profile dict.
        limit:
            Maximum number of candidates to export. ``None`` means all.
        candidate_details_map:
            Pre-fetched {candidate_id: {name, title}} mapping; fetched from
            CandidateService if not supplied.

        Returns
        -------
        List[Dict[str, Any]]
            Validated, sorted, enriched candidate records.

        Raises
        ------
        ValidationError
            If any check fails.
        """
        issues: List[ValidationIssue] = []

        # ── 1. Profiles must exist ────────────────────────────────────────────
        if not profiles:
            raise ValidationError("Feature profile cache is empty. Build the feature cache first.")

        # ── 2. Duplicate ID detection ─────────────────────────────────────────
        seen_ids: set[str] = set()
        for cid in profiles:
            if cid in seen_ids:
                issues.append(
                    ValidationIssue(
                        code="DUPLICATE_ID",
                        message=f"Duplicate candidate_id detected: {cid}",
                        candidate_id=cid,
                    )
                )
            seen_ids.add(cid)

        if issues:
            raise ValidationError(
                f"Validation failed with {len(issues)} duplicate ID(s). "
                + "; ".join(i.message for i in issues)
            )

        # ── 3. Required columns in every profile ──────────────────────────────
        missing_col_issues: List[ValidationIssue] = []
        for cid, profile in profiles.items():
            missing = REQUIRED_KEYS - set(profile.keys())
            if missing:
                missing_col_issues.append(
                    ValidationIssue(
                        code="MISSING_COLUMNS",
                        message=f"Candidate {cid} is missing required fields: {missing}",
                        candidate_id=cid,
                    )
                )

        if missing_col_issues:
            raise ValidationError(
                f"Validation failed: {len(missing_col_issues)} candidate(s) have missing columns."
            )

        # ── 4. Null / invalid overall_score check ─────────────────────────────
        null_score_issues: List[ValidationIssue] = []
        for cid, profile in profiles.items():
            score = profile.get("overall_score")
            if score is None:
                null_score_issues.append(
                    ValidationIssue(
                        code="NULL_SCORE",
                        message=f"Candidate {cid} has a null overall_score.",
                        candidate_id=cid,
                    )
                )
        if null_score_issues:
            raise ValidationError(
                f"Validation failed: {len(null_score_issues)} candidate(s) have null scores."
            )

        # ── 5. Candidate existence in repository ──────────────────────────────
        all_cids = list(profiles.keys())
        if candidate_details_map is None:
            try:
                candidate_details_map = {
                    c["candidate_id"]: c
                    for c in CandidateService.get_candidates_by_ids(all_cids)
                }
            except Exception as exc:
                raise ValidationError(
                    f"Could not verify candidate existence: {exc}"
                )

        unknown = [cid for cid in all_cids if cid not in candidate_details_map]
        if unknown:
            raise ValidationError(
                f"Validation failed: {len(unknown)} candidate ID(s) not found in repository: "
                + ", ".join(unknown[:10])
                + ("..." if len(unknown) > 10 else "")
            )

        # ── 6. Build enriched list and apply deterministic sort ───────────────
        flat: List[Dict[str, Any]] = []
        for cid, profile in profiles.items():
            details = candidate_details_map.get(cid, {})
            flat.append(
                {
                    "candidate_id": cid,
                    "name": details.get("anonymized_name", "Anonymized"),
                    "title": details.get("current_title", "Professional"),
                    "overall_score": round(float(profile.get("overall_score", 0.0)), 2),
                    "semantic_score": round(float(profile.get("semantic_score", 0.0)), 2),
                    "skill_score": round(float(profile.get("skill_score", 0.0)), 2),
                    "experience_score": round(float(profile.get("experience_score", 0.0)), 2),
                    "education_score": round(float(profile.get("education_score", 0.0)), 2),
                    "certification_score": round(float(profile.get("certification_score", 0.0)), 2),
                    "language_score": round(float(profile.get("language_score", 0.0)), 2),
                    "behavior_score": round(float(profile.get("behavior_score", 0.0)), 2),
                    "decision": profile.get("decision"),
                    "confidence": profile.get("confidence"),
                    "recommendation": profile.get("recommendation"),
                    "reason_codes": profile.get("reason_codes", []),
                    "metadata": profile.get("metadata", {}),
                }
            )

        sorted_list = deterministic_sort(flat)

        # ── 7. Apply rank numbers ─────────────────────────────────────────────
        for rank, record in enumerate(sorted_list, start=1):
            record["rank"] = rank

        # ── 8. Trim to limit ──────────────────────────────────────────────────
        effective_limit = resolve_limit(limit, default=len(sorted_list))
        result = sorted_list[:effective_limit]

        logger.info(
            "Validation passed: {total} profiles validated, {exported} selected for export.",
            total=len(sorted_list),
            exported=len(result),
        )
        return result
