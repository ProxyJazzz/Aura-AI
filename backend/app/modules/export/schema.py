"""
Pydantic schema definitions for the Export / Submission Engine module.

Covers request payloads, response envelopes, manifest, and history entries.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────


class ExportType(str, Enum):
    CSV = "csv"
    JSON = "json"
    REPORT = "report"


# ── Request Models ────────────────────────────────────────────────────────────


class ExportRequest(BaseModel):
    """Request payload for all export endpoints."""

    profile: Optional[str] = Field(
        default=None,
        description="Weight profile name; defaults to system default.",
    )
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        le=100_000,
        description="Number of top candidates to export. "
                    "Supported shortcuts: 10, 25, 50, 100, or any custom int.",
    )
    export_type: ExportType = Field(
        ...,
        description="One of 'csv', 'json', 'report'.",
    )


class ValidateRequest(BaseModel):
    """Request payload for the validation endpoint."""

    profile: Optional[str] = Field(
        default=None,
        description="Weight profile name to validate against.",
    )
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        description="Restrict validation to the top‑N ranked candidates.",
    )


# ── Response Models ───────────────────────────────────────────────────────────


class ExportResponse(BaseModel):
    """Lightweight acknowledgement returned from async export endpoints."""

    detail: str
    export_id: Optional[str] = None
    checksum: Optional[str] = None
    filename: Optional[str] = None


class ValidationIssue(BaseModel):
    """A single validation failure detail."""

    code: str
    message: str
    candidate_id: Optional[str] = None


class ValidationResponse(BaseModel):
    """Response from the POST /export/validate endpoint."""

    valid: bool
    candidate_count: int
    issues: List[ValidationIssue] = Field(default_factory=list)


class ExportStatusResponse(BaseModel):
    """Response from GET /export/status."""

    last_export_type: Optional[str] = None
    last_export_at: Optional[str] = None
    last_export_candidate_count: Optional[int] = None
    last_checksum: Optional[str] = None
    total_exports: int = 0


# ── Manifest ──────────────────────────────────────────────────────────────────


class Manifest(BaseModel):
    """Submission manifest written alongside every export artifact."""

    project_name: str = "AURA AI"
    version: str
    generated_at: str
    job_id: str
    ranking_profile: str
    candidates_exported: int
    checksum: str


# ── History ───────────────────────────────────────────────────────────────────


class ExportHistoryEntry(BaseModel):
    """One row in the export history table."""

    export_id: str
    timestamp: str
    export_type: str
    user: Optional[str] = None
    candidate_count: int
    duration_ms: int
    checksum: str
    profile: Optional[str] = None


# ── Internal Data Transfer ────────────────────────────────────────────────────


class RankedCandidate(BaseModel):
    """Internal DTO representing a fully‑resolved ranked candidate."""

    rank: int
    candidate_id: str
    name: str
    title: str
    overall_score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    education_score: float
    certification_score: float
    language_score: float
    behavior_score: float
    decision: Optional[str] = None
    confidence: Optional[float] = None
    recommendation: Optional[str] = None
    reason_codes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
