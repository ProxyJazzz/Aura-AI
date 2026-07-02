"""
Export Service — Orchestration layer for the Submission Engine.

Responsibilities
----------------
- Load feature profiles from FeatureService (single source of truth for scores).
- Enrich profiles with candidate metadata from CandidateService.
- Delegate pre-export validation to SubmissionValidator.
- Call the appropriate exporter (CSV / JSON / Report).
- Generate the submission manifest.
- Persist every artifact + history row via ExportCacheService.
- Expose clean async methods consumed by the FastAPI router.

Design decisions
----------------
- All heavy I/O (candidate list fetch, validation, export) is wrapped in
  asyncio.to_thread so the ASGI event loop is never blocked.
- FeatureService is the **sole** source of scores; no ranking logic is
  duplicated here.
- The service returns FastAPI StreamingResponse objects so callers can
  download artifacts directly.
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi.responses import StreamingResponse
from loguru import logger

from app.modules.candidates.service import CandidateService
from app.modules.export.cache_service import ExportCacheService
from app.modules.export.csv_exporter import CSVExporter
from app.modules.export.exceptions import ExportServiceIntegrationError, ValidationError
from app.modules.export.json_exporter import JSONExporter
from app.modules.export.report_exporter import ReportExporter
from app.modules.export.schema import (
    ExportHistoryEntry,
    ExportStatusResponse,
    Manifest,
    ValidationResponse,
    ValidationIssue,
)
from app.modules.export.utils import (
    AURA_VERSION,
    compute_checksum,
    resolve_limit,
    resolve_profile,
)
from app.modules.export.validator import SubmissionValidator
from app.modules.features.service import FeatureService
from app.modules.jobs.service import JobService


# ── Internal helpers ──────────────────────────────────────────────────────────


def _load_profiles() -> Dict[str, Dict[str, Any]]:
    """Load feature profiles from the FeatureService RAM cache (blocking)."""
    try:
        FeatureService.load_cache_into_memory()
        profiles = FeatureService._cached_profiles or {}
        if not profiles:
            raise ExportServiceIntegrationError(
                "Feature profile cache is empty. Run POST /features/build first."
            )
        return profiles
    except Exception as exc:
        raise ExportServiceIntegrationError(f"Failed to load feature profiles: {exc}")


def _build_candidate_details_map(cids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch candidate metadata rows and index by candidate_id."""
    try:
        rows = CandidateService.get_candidates_by_ids(cids)
        return {r["candidate_id"]: r for r in rows}
    except Exception as exc:
        raise ExportServiceIntegrationError(f"CandidateService lookup failed: {exc}")


def _build_manifest(
    *,
    job_id: str,
    profile: str,
    candidate_count: int,
    checksum: str,
) -> Manifest:
    return Manifest(
        version=AURA_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        job_id=job_id,
        ranking_profile=profile,
        candidates_exported=candidate_count,
        checksum=checksum,
    )


# ── Public Service ────────────────────────────────────────────────────────────


class ExportService:
    """Async-first orchestration service for all export operations."""

    # ── Validate ─────────────────────────────────────────────────────────────

    @staticmethod
    async def validate_export(
        profile: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> ValidationResponse:
        """
        Run pre-export validation without generating any artifact.
        Returns a ValidationResponse indicating pass/fail + issues list.
        """

        def _run() -> ValidationResponse:
            resolved_profile = resolve_profile(profile)
            try:
                profiles = _load_profiles()
                all_cids = list(profiles.keys())
                details_map = _build_candidate_details_map(all_cids)
                SubmissionValidator.validate(
                    profiles, limit=limit, candidate_details_map=details_map
                )
                return ValidationResponse(
                    valid=True,
                    candidate_count=resolve_limit(limit, default=len(profiles)),
                )
            except ValidationError as ve:
                return ValidationResponse(
                    valid=False,
                    candidate_count=0,
                    issues=[ValidationIssue(code="VALIDATION_FAILED", message=ve.detail)],
                )

        return await asyncio.to_thread(_run)

    # ── CSV Export ────────────────────────────────────────────────────────────

    @staticmethod
    async def export_csv(
        profile: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> StreamingResponse:
        """
        Generate the official Hack2Skill CSV artifact.
        Returns a StreamingResponse for direct download.
        """

        def _run() -> tuple[str, str, str, int, str]:
            resolved_profile = resolve_profile(profile)
            effective_limit = resolve_limit(limit, default=100)

            start = time.perf_counter()
            profiles = _load_profiles()
            all_cids = list(profiles.keys())
            details_map = _build_candidate_details_map(all_cids)
            validated = SubmissionValidator.validate(
                profiles, limit=effective_limit, candidate_details_map=details_map
            )
            csv_content, checksum = CSVExporter.export(validated)
            duration_ms = int((time.perf_counter() - start) * 1000)
            filename = CSVExporter.filename(effective_limit, resolved_profile)

            ExportCacheService.store_export(
                export_type="csv",
                profile=resolved_profile,
                blob=csv_content.encode("utf-8"),
                filename=filename,
                checksum=checksum,
                candidate_count=len(validated),
                duration_ms=duration_ms,
            )
            logger.info(
                "CSV export complete: {n} candidates, {ms}ms, checksum={ck}",
                n=len(validated),
                ms=duration_ms,
                ck=checksum[:8],
            )
            return csv_content, filename, checksum, len(validated), resolved_profile

        csv_content, filename, checksum, n, resolved_profile = await asyncio.to_thread(_run)

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Checksum-SHA256": checksum,
                "X-Candidate-Count": str(n),
            },
        )

    # ── JSON Export ───────────────────────────────────────────────────────────

    @staticmethod
    async def export_json(
        profile: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> StreamingResponse:
        """Generate the complete AI output JSON export."""

        def _run() -> tuple[str, str, str, int]:
            resolved_profile = resolve_profile(profile)
            effective_limit = resolve_limit(limit, default=100)

            start = time.perf_counter()
            profiles = _load_profiles()
            all_cids = list(profiles.keys())
            details_map = _build_candidate_details_map(all_cids)
            validated = SubmissionValidator.validate(
                profiles, limit=effective_limit, candidate_details_map=details_map
            )
            json_content, checksum = JSONExporter.export(validated, resolved_profile)
            duration_ms = int((time.perf_counter() - start) * 1000)
            filename = JSONExporter.filename(effective_limit, resolved_profile)

            ExportCacheService.store_export(
                export_type="json",
                profile=resolved_profile,
                blob=json_content.encode("utf-8"),
                filename=filename,
                checksum=checksum,
                candidate_count=len(validated),
                duration_ms=duration_ms,
            )
            logger.info(
                "JSON export complete: {n} candidates, {ms}ms",
                n=len(validated),
                ms=duration_ms,
            )
            return json_content, filename, checksum, len(validated)

        json_content, filename, checksum, n = await asyncio.to_thread(_run)

        return StreamingResponse(
            iter([json_content]),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Checksum-SHA256": checksum,
                "X-Candidate-Count": str(n),
            },
        )

    # ── Recruiter Report ──────────────────────────────────────────────────────

    @staticmethod
    async def export_report(
        profile: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> StreamingResponse:
        """Generate the recruiter intelligence report JSON."""

        def _run() -> tuple[str, str, str, int]:
            resolved_profile = resolve_profile(profile)
            effective_limit = resolve_limit(limit, default=100)

            start = time.perf_counter()
            profiles = _load_profiles()
            all_cids = list(profiles.keys())
            details_map = _build_candidate_details_map(all_cids)
            validated = SubmissionValidator.validate(
                profiles, limit=effective_limit, candidate_details_map=details_map
            )

            # Fetch job info (non-fatal if unavailable)
            active_job: Optional[Dict[str, Any]] = None
            try:
                active_job = JobService.get_active_job()
            except Exception:
                logger.warning("Could not fetch active job for report. Proceeding without job info.")

            report_content, checksum = ReportExporter.export(validated, active_job, resolved_profile)
            duration_ms = int((time.perf_counter() - start) * 1000)
            filename = ReportExporter.filename(resolved_profile)

            ExportCacheService.store_export(
                export_type="report",
                profile=resolved_profile,
                blob=report_content.encode("utf-8"),
                filename=filename,
                checksum=checksum,
                candidate_count=len(validated),
                duration_ms=duration_ms,
            )
            logger.info(
                "Report export complete: {n} candidates, {ms}ms",
                n=len(validated),
                ms=duration_ms,
            )
            return report_content, filename, checksum, len(validated)

        report_content, filename, checksum, n = await asyncio.to_thread(_run)

        return StreamingResponse(
            iter([report_content]),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Checksum-SHA256": checksum,
                "X-Candidate-Count": str(n),
            },
        )

    # ── Manifest ──────────────────────────────────────────────────────────────

    @staticmethod
    async def generate_manifest(
        checksum: str,
        candidate_count: int,
        profile: Optional[str] = None,
    ) -> Manifest:
        """Build and return the submission manifest (does not persist to cache)."""

        def _run() -> Manifest:
            resolved_profile = resolve_profile(profile)
            job_id = "unknown"
            try:
                job = JobService.get_active_job()
                if job:
                    job_id = str(job.get("id", "unknown"))
            except Exception:
                pass

            return _build_manifest(
                job_id=job_id,
                profile=resolved_profile,
                candidate_count=candidate_count,
                checksum=checksum,
            )

        return await asyncio.to_thread(_run)

    # ── History ───────────────────────────────────────────────────────────────

    @staticmethod
    async def get_history(limit: int = 50) -> List[ExportHistoryEntry]:
        """Return the most recent export history entries."""

        def _run() -> List[ExportHistoryEntry]:
            rows = ExportCacheService.list_history(limit=limit)
            return [
                ExportHistoryEntry(
                    export_id=r["export_id"],
                    timestamp=r["created_at"],
                    export_type=r["export_type"],
                    user=r.get("user_id"),
                    candidate_count=r["candidate_count"],
                    duration_ms=r["duration_ms"],
                    checksum=r["checksum"],
                    profile=r.get("profile"),
                )
                for r in rows
            ]

        return await asyncio.to_thread(_run)

    # ── Status ────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_status() -> ExportStatusResponse:
        """Return high-level export cache statistics."""

        def _run() -> ExportStatusResponse:
            status = ExportCacheService.get_status()
            return ExportStatusResponse(**status)

        return await asyncio.to_thread(_run)

    # ── Clear cache ───────────────────────────────────────────────────────────

    @staticmethod
    async def clear_cache(profile: Optional[str] = None) -> None:
        """Clear export artifacts (and history) for a profile or all."""
        await asyncio.to_thread(ExportCacheService.clear_cache, profile)
