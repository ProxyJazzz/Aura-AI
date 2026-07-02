"""
FastAPI Router for the Export / Submission Engine.

Endpoints
---------
GET  /export/csv        — Download Hack2Skill submission CSV
GET  /export/json       — Download complete AI output JSON
GET  /export/report     — Download recruiter intelligence report
GET  /export/manifest   — Generate and return submission manifest JSON
GET  /export/history    — List recent export history
POST /export/validate   — Validate without generating an artifact
GET  /export/status     — Return export cache statistics
DELETE /export/cache    — Clear export cache (all or by profile)
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from loguru import logger

from app.modules.export.exceptions import (
    ExportError,
    ExportServiceIntegrationError,
    ValidationError,
)
from app.modules.export.schema import (
    ExportHistoryEntry,
    ExportStatusResponse,
    Manifest,
    ValidateRequest,
    ValidationResponse,
)
from app.modules.export.service import ExportService

router = APIRouter(tags=["Export"])


# ── CSV ───────────────────────────────────────────────────────────────────────


@router.get(
    "/export/csv",
    response_class=StreamingResponse,
    summary="Download Hack2Skill submission CSV",
    description=(
        "Validates ranking output and generates the official Hack2Skill submission CSV. "
        "Supported limit shortcuts: 10, 25, 50, 100 or any custom integer. "
        "Always sorted by rank ascending."
    ),
)
async def export_csv(
    limit: Optional[int] = Query(None, ge=1, le=100_000, description="Top-N candidates to export."),
    profile: Optional[str] = Query(None, description="Weight profile name."),
) -> StreamingResponse:
    try:
        return await ExportService.export_csv(profile=profile, limit=limit)
    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.detail)
    except ExportServiceIntegrationError as ie:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(ie))
    except ExportError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── JSON ──────────────────────────────────────────────────────────────────────


@router.get(
    "/export/json",
    response_class=StreamingResponse,
    summary="Download complete AI output JSON",
    description=(
        "Exports the full AI intelligence output per candidate: scores, decision, "
        "confidence, recommendation, reason codes, feature scores, semantic score, and metadata."
    ),
)
async def export_json(
    limit: Optional[int] = Query(None, ge=1, le=100_000),
    profile: Optional[str] = Query(None),
) -> StreamingResponse:
    try:
        return await ExportService.export_json(profile=profile, limit=limit)
    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.detail)
    except ExportServiceIntegrationError as ie:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(ie))
    except ExportError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Recruiter Report ──────────────────────────────────────────────────────────


@router.get(
    "/export/report",
    response_class=StreamingResponse,
    summary="Download recruiter intelligence report",
    description=(
        "Generates a recruiter-facing JSON report including job summary, "
        "top candidates, score analytics, recommendation summary, and hiring statistics."
    ),
)
async def export_report(
    limit: Optional[int] = Query(None, ge=1, le=100_000),
    profile: Optional[str] = Query(None),
) -> StreamingResponse:
    try:
        return await ExportService.export_report(profile=profile, limit=limit)
    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.detail)
    except ExportServiceIntegrationError as ie:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(ie))
    except ExportError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Submission Manifest ───────────────────────────────────────────────────────


@router.get(
    "/export/manifest",
    response_model=Manifest,
    summary="Generate submission manifest",
    description=(
        "Returns the submission.json manifest describing the export artifact: "
        "project name, version, generated_at, job_id, ranking_profile, "
        "candidate count, and checksum."
    ),
)
async def get_manifest(
    checksum: str = Query(..., description="SHA-256 checksum of the export artifact."),
    candidate_count: int = Query(..., ge=1),
    profile: Optional[str] = Query(None),
) -> Manifest:
    try:
        return await ExportService.generate_manifest(
            checksum=checksum, candidate_count=candidate_count, profile=profile
        )
    except ExportError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── History ───────────────────────────────────────────────────────────────────


@router.get(
    "/export/history",
    response_model=List[ExportHistoryEntry],
    summary="List export history",
    description="Returns the most recent export events (newest first).",
)
async def get_history(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of history entries to return."),
) -> List[ExportHistoryEntry]:
    try:
        return await ExportService.get_history(limit=limit)
    except ExportError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Validate ──────────────────────────────────────────────────────────────────


@router.post(
    "/export/validate",
    response_model=ValidationResponse,
    summary="Validate export without generating artifact",
    description=(
        "Runs all pre-export checks (duplicate IDs, missing candidates, "
        "null scores, required columns, ranking order) and returns a "
        "pass/fail response with detailed issue list."
    ),
)
async def validate_export(request: ValidateRequest) -> ValidationResponse:
    try:
        return await ExportService.validate_export(
            profile=request.profile, limit=request.limit
        )
    except ExportServiceIntegrationError as ie:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(ie))
    except ExportError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Status ────────────────────────────────────────────────────────────────────


@router.get(
    "/export/status",
    response_model=ExportStatusResponse,
    summary="Export cache status",
    description="Returns metadata about the last export event and total export count.",
)
async def get_status() -> ExportStatusResponse:
    try:
        return await ExportService.get_status()
    except ExportError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ── Clear Cache ───────────────────────────────────────────────────────────────


@router.delete(
    "/export/cache",
    response_model=dict,
    summary="Clear export cache",
    description="Deletes cached export artifacts and history rows for the given profile (or all).",
)
async def clear_cache(
    profile: Optional[str] = Query(None, description="Profile to clear; omit to clear all."),
) -> dict:
    try:
        await ExportService.clear_cache(profile=profile)
        return {"detail": f"Export cache cleared (profile={profile or 'ALL'})."}
    except ExportError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
