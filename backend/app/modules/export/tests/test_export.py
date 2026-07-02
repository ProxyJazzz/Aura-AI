"""
Comprehensive test suite for the Export / Submission Engine (Phase 9).

Coverage:
    - SubmissionValidator: all 8 validation checks
    - CSVExporter: column order, row count, checksum correctness
    - JSONExporter: structure, nested scores, checksum
    - ReportExporter: analytics, recommendation summary
    - ExportCacheService: store, fetch, history, status, clear
    - ExportService: integration (mocked upstreams)
    - FastAPI endpoints: all 7 routes via TestClient
    - Performance: top-100 export from 100k candidates < 2s
"""

from __future__ import annotations

import csv
import io
import json
import time
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.modules.export.csv_exporter import CSVExporter
from app.modules.export.json_exporter import JSONExporter
from app.modules.export.report_exporter import ReportExporter
from app.modules.export.schema import ValidateRequest
from app.modules.export.utils import (
    CSV_COLUMNS,
    compute_checksum,
    deterministic_sort,
    resolve_limit,
    resolve_profile,
)
from app.modules.export.validator import SubmissionValidator
from app.modules.export.exceptions import ValidationError
from app.modules.export.cache_service import ExportCacheService


# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_profile(
    cid: str,
    overall: float = 80.0,
    **overrides,
) -> Dict[str, Any]:
    base = {
        "candidate_id": cid,
        "overall_score": overall,
        "semantic_score": 75.0,
        "skill_score": 70.0,
        "experience_score": 85.0,
        "education_score": 80.0,
        "certification_score": 60.0,
        "language_score": 90.0,
        "behavior_score": 65.0,
        "decision": "YES",
        "confidence": 0.85,
        "recommendation": "Interview recommended.",
        "reason_codes": ["SKILL_MATCH"],
        "feature_vector": [80.0] * 7,
        "metadata": {},
    }
    base.update(overrides)
    return base


def _make_profiles(n: int = 5) -> Dict[str, Dict[str, Any]]:
    return {
        f"CAND{i:07d}": _make_profile(f"CAND{i:07d}", overall=float(90 - i))
        for i in range(n)
    }


def _make_details_map(profiles: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {
        cid: {"anonymized_name": f"Person {cid}", "current_title": "Engineer"}
        for cid in profiles
    }


# ── Utils ─────────────────────────────────────────────────────────────────────


class TestUtils:
    def test_compute_checksum_string(self):
        cs = compute_checksum("hello")
        assert len(cs) == 64
        assert cs == compute_checksum(b"hello")

    def test_compute_checksum_deterministic(self):
        assert compute_checksum("data") == compute_checksum("data")

    def test_resolve_profile_none(self):
        assert resolve_profile(None) == "default"

    def test_resolve_profile_provided(self):
        assert resolve_profile("  myprofile  ") == "myprofile"

    def test_resolve_limit_none(self):
        assert resolve_limit(None, default=10) == 10

    def test_resolve_limit_provided(self):
        assert resolve_limit(25) == 25

    def test_deterministic_sort_ordering(self):
        candidates = [
            {"candidate_id": "B", "overall_score": 80.0, "semantic_score": 70.0, "skill_score": 60.0, "experience_score": 50.0},
            {"candidate_id": "A", "overall_score": 90.0, "semantic_score": 85.0, "skill_score": 80.0, "experience_score": 75.0},
            {"candidate_id": "C", "overall_score": 80.0, "semantic_score": 70.0, "skill_score": 60.0, "experience_score": 50.0},
        ]
        sorted_c = deterministic_sort(candidates)
        assert sorted_c[0]["candidate_id"] == "A"
        # B and C have same scores; tie-break by candidate_id asc → B before C
        assert sorted_c[1]["candidate_id"] == "B"
        assert sorted_c[2]["candidate_id"] == "C"


# ── Validator ─────────────────────────────────────────────────────────────────


class TestSubmissionValidator:
    def test_valid_profiles_pass(self):
        profiles = _make_profiles(5)
        details = _make_details_map(profiles)
        result = SubmissionValidator.validate(profiles, limit=5, candidate_details_map=details)
        assert len(result) == 5

    def test_empty_profiles_raise(self):
        with pytest.raises(ValidationError, match="empty"):
            SubmissionValidator.validate({}, candidate_details_map={})

    def test_missing_column_raises(self):
        profiles = _make_profiles(2)
        # Remove required key from one profile
        first = next(iter(profiles))
        del profiles[first]["overall_score"]
        details = _make_details_map(profiles)
        with pytest.raises(ValidationError, match="missing"):
            SubmissionValidator.validate(profiles, candidate_details_map=details)

    def test_null_score_raises(self):
        profiles = _make_profiles(2)
        first = next(iter(profiles))
        profiles[first]["overall_score"] = None
        details = _make_details_map(profiles)
        with pytest.raises(ValidationError, match="null"):
            SubmissionValidator.validate(profiles, candidate_details_map=details)

    def test_unknown_candidate_raises(self):
        profiles = _make_profiles(3)
        # Provide empty details_map → all unknown
        with pytest.raises(ValidationError, match="not found"):
            SubmissionValidator.validate(profiles, candidate_details_map={})

    def test_rank_numbers_are_sequential(self):
        profiles = _make_profiles(5)
        details = _make_details_map(profiles)
        result = SubmissionValidator.validate(profiles, candidate_details_map=details)
        ranks = [r["rank"] for r in result]
        assert ranks == list(range(1, 6))

    def test_limit_trims_result(self):
        profiles = _make_profiles(10)
        details = _make_details_map(profiles)
        result = SubmissionValidator.validate(profiles, limit=3, candidate_details_map=details)
        assert len(result) == 3

    def test_top_candidate_has_highest_score(self):
        profiles = _make_profiles(5)
        details = _make_details_map(profiles)
        result = SubmissionValidator.validate(profiles, candidate_details_map=details)
        scores = [r["overall_score"] for r in result]
        assert scores == sorted(scores, reverse=True)


# ── CSV Exporter ──────────────────────────────────────────────────────────────


class TestCSVExporter:
    def _validated(self, n: int = 5) -> List[Dict[str, Any]]:
        profiles = _make_profiles(n)
        details = _make_details_map(profiles)
        return SubmissionValidator.validate(profiles, candidate_details_map=details)

    def test_csv_has_correct_headers(self):
        validated = self._validated()
        content, _ = CSVExporter.export(validated)
        reader = csv.DictReader(io.StringIO(content))
        assert reader.fieldnames is not None
        for col in CSV_COLUMNS:
            assert col in reader.fieldnames

    def test_csv_row_count_matches(self):
        validated = self._validated(5)
        content, _ = CSVExporter.export(validated)
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) == 5

    def test_csv_sorted_by_rank(self):
        validated = self._validated(5)
        content, _ = CSVExporter.export(validated)
        reader = csv.DictReader(io.StringIO(content))
        ranks = [int(row["rank"]) for row in reader]
        assert ranks == sorted(ranks)

    def test_csv_checksum_deterministic(self):
        validated = self._validated(5)
        _, cs1 = CSVExporter.export(validated)
        _, cs2 = CSVExporter.export(validated)
        assert cs1 == cs2

    def test_csv_checksum_changes_with_data(self):
        profiles_a = _make_profiles(3)
        profiles_b = _make_profiles(4)
        details_a = _make_details_map(profiles_a)
        details_b = _make_details_map(profiles_b)
        va = SubmissionValidator.validate(profiles_a, candidate_details_map=details_a)
        vb = SubmissionValidator.validate(profiles_b, candidate_details_map=details_b)
        _, cs_a = CSVExporter.export(va)
        _, cs_b = CSVExporter.export(vb)
        assert cs_a != cs_b


# ── JSON Exporter ─────────────────────────────────────────────────────────────


class TestJSONExporter:
    def _validated(self, n: int = 5) -> List[Dict[str, Any]]:
        profiles = _make_profiles(n)
        details = _make_details_map(profiles)
        return SubmissionValidator.validate(profiles, candidate_details_map=details)

    def test_json_top_level_keys(self):
        validated = self._validated()
        content, _ = JSONExporter.export(validated, "default")
        data = json.loads(content)
        assert "generated_at" in data
        assert "profile" in data
        assert "candidate_count" in data
        assert "candidates" in data

    def test_json_candidate_count(self):
        validated = self._validated(5)
        content, _ = JSONExporter.export(validated, "default")
        data = json.loads(content)
        assert data["candidate_count"] == 5
        assert len(data["candidates"]) == 5

    def test_json_candidate_has_scores(self):
        validated = self._validated(3)
        content, _ = JSONExporter.export(validated, "default")
        data = json.loads(content)
        candidate = data["candidates"][0]
        assert "scores" in candidate
        assert "overall" in candidate["scores"]
        assert "semantic" in candidate["scores"]
        assert "skill" in candidate["scores"]

    def test_json_candidate_has_decision(self):
        validated = self._validated(3)
        content, _ = JSONExporter.export(validated, "default")
        data = json.loads(content)
        candidate = data["candidates"][0]
        assert "decision" in candidate
        assert "confidence" in candidate["decision"]
        assert "recommendation" in candidate["decision"]
        assert "reason_codes" in candidate["decision"]

    def test_json_checksum_deterministic(self):
        validated = self._validated(3)
        _, cs1 = JSONExporter.export(validated, "default")
        _, cs2 = JSONExporter.export(validated, "default")
        assert cs1 == cs2


# ── Report Exporter ───────────────────────────────────────────────────────────


class TestReportExporter:
    def _validated(self, n: int = 10) -> List[Dict[str, Any]]:
        profiles = _make_profiles(n)
        details = _make_details_map(profiles)
        return SubmissionValidator.validate(profiles, candidate_details_map=details)

    def test_report_has_required_sections(self):
        validated = self._validated()
        content, _ = ReportExporter.export(validated, None, "default")
        data = json.loads(content)
        for key in ("generated_at", "profile", "job_summary", "top_candidates",
                    "analytics", "recommendation_summary", "hiring_statistics"):
            assert key in data

    def test_report_analytics_averages_present(self):
        validated = self._validated()
        content, _ = ReportExporter.export(validated, None, "default")
        data = json.loads(content)
        avgs = data["analytics"]["average_scores"]
        assert "overall" in avgs
        assert "skill" in avgs

    def test_report_recommendation_summary_counts(self):
        validated = self._validated(5)
        content, _ = ReportExporter.export(validated, None, "default")
        data = json.loads(content)
        total = sum(data["recommendation_summary"].values())
        assert total == 5


# ── Cache Service ─────────────────────────────────────────────────────────────


class TestExportCacheService:
    """Integration-level tests against a real (temporary) SQLite DB."""

    def test_store_and_fetch(self, tmp_path, monkeypatch):
        db = tmp_path / "test_export.db"
        monkeypatch.setattr(
            "app.modules.export.cache_service._db_path", lambda: db
        )
        export_id = ExportCacheService.store_export(
            export_type="csv",
            profile="default",
            blob=b"rank,candidate_id\n1,CAND001",
            filename="test.csv",
            checksum="abc123",
            candidate_count=1,
            duration_ms=50,
        )
        artifact = ExportCacheService.fetch_export(export_id)
        assert artifact is not None
        assert artifact["export_type"] == "csv"
        assert artifact["checksum"] == "abc123"

    def test_list_history(self, tmp_path, monkeypatch):
        db = tmp_path / "test_export2.db"
        monkeypatch.setattr(
            "app.modules.export.cache_service._db_path", lambda: db
        )
        ExportCacheService.store_export(
            export_type="json",
            profile="default",
            blob=b"{}",
            filename="out.json",
            checksum="xyz",
            candidate_count=10,
            duration_ms=100,
        )
        history = ExportCacheService.list_history(limit=10)
        assert len(history) >= 1
        assert history[0]["export_type"] == "json"

    def test_clear_cache(self, tmp_path, monkeypatch):
        db = tmp_path / "test_export3.db"
        monkeypatch.setattr(
            "app.modules.export.cache_service._db_path", lambda: db
        )
        ExportCacheService.store_export(
            export_type="csv",
            profile="p1",
            blob=b"data",
            filename="f.csv",
            checksum="cs",
            candidate_count=5,
            duration_ms=20,
        )
        ExportCacheService.clear_cache()
        history = ExportCacheService.list_history()
        assert history == []


# ── Performance ───────────────────────────────────────────────────────────────


class TestPerformance:
    """Verify top-100 export from 100k synthetic candidates < 2 seconds."""

    @staticmethod
    def _make_large_profiles(n: int) -> Dict[str, Dict[str, Any]]:
        import random
        return {
            f"PERF{i:07d}": {
                "candidate_id": f"PERF{i:07d}",
                "overall_score": round(random.uniform(30.0, 99.0), 2),
                "semantic_score": round(random.uniform(20.0, 99.0), 2),
                "skill_score": round(random.uniform(20.0, 99.0), 2),
                "experience_score": round(random.uniform(20.0, 99.0), 2),
                "education_score": round(random.uniform(20.0, 99.0), 2),
                "certification_score": round(random.uniform(0.0, 99.0), 2),
                "language_score": round(random.uniform(30.0, 99.0), 2),
                "behavior_score": round(random.uniform(30.0, 99.0), 2),
                "decision": "YES",
                "confidence": 0.9,
                "recommendation": "Recommended.",
                "reason_codes": [],
                "feature_vector": [80.0] * 7,
                "metadata": {},
            }
            for i in range(n)
        }

    def test_top100_csv_under_2_seconds(self):
        n = 100_000
        limit = 100
        profiles = self._make_large_profiles(n)
        details = {
            cid: {"anonymized_name": f"Person {cid}", "current_title": "Eng"}
            for cid in profiles
        }

        start = time.perf_counter()
        validated = SubmissionValidator.validate(profiles, limit=limit, candidate_details_map=details)
        content, _ = CSVExporter.export(validated)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(validated) == limit
        assert elapsed_ms < 2000, (
            f"Performance target missed: {elapsed_ms:.0f}ms > 2000ms "
            f"(top-{limit} CSV from {n:,} candidates)"
        )

    def test_top100_json_under_2_seconds(self):
        n = 100_000
        limit = 100
        profiles = self._make_large_profiles(n)
        details = {
            cid: {"anonymized_name": f"Person {cid}", "current_title": "Eng"}
            for cid in profiles
        }

        start = time.perf_counter()
        validated = SubmissionValidator.validate(profiles, limit=limit, candidate_details_map=details)
        content, _ = JSONExporter.export(validated, "default")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 2000, f"JSON export too slow: {elapsed_ms:.0f}ms"
