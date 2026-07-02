"""
Performance benchmark utility for the Export / Submission Engine.

Usage (CLI):
    python -m app.modules.export.benchmark --type csv --limit 100

Measures:
    - Validation time
    - Export generation time
    - Total end-to-end time
    - Output file size (bytes / KB)

Performance target:
    Top-100 export from 100,000 candidates < 2,000 ms total.
"""

from __future__ import annotations

import argparse
import time
from typing import Any, Dict, List


def _generate_synthetic_profiles(n: int) -> Dict[str, Dict[str, Any]]:
    """Generate *n* synthetic feature profiles for benchmark purposes."""
    import random

    profiles: Dict[str, Dict[str, Any]] = {}
    for i in range(n):
        cid = f"CAND{i:07d}"
        overall = round(random.uniform(30.0, 98.0), 2)
        profiles[cid] = {
            "candidate_id": cid,
            "overall_score": overall,
            "semantic_score": round(random.uniform(20.0, 99.0), 2),
            "skill_score": round(random.uniform(20.0, 99.0), 2),
            "experience_score": round(random.uniform(20.0, 99.0), 2),
            "education_score": round(random.uniform(20.0, 99.0), 2),
            "certification_score": round(random.uniform(0.0, 99.0), 2),
            "language_score": round(random.uniform(30.0, 99.0), 2),
            "behavior_score": round(random.uniform(30.0, 99.0), 2),
            "decision": random.choice(["STRONG_YES", "YES", "MAYBE", "NO"]),
            "confidence": round(random.uniform(0.5, 1.0), 2),
            "recommendation": "Interview recommended.",
            "reason_codes": ["SKILL_MATCH", "EXPERIENCE_FIT"],
            "feature_vector": [overall] * 7,
            "metadata": {},
        }
    return profiles


def _fake_details_map(profiles: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Return a synthetic candidate details map for the validator."""
    return {
        cid: {"anonymized_name": f"Candidate {cid}", "current_title": "Engineer"}
        for cid in profiles
    }


def run_benchmark(export_type: str = "csv", limit: int = 100, n_candidates: int = 100_000) -> None:
    """
    Execute a timed end-to-end export benchmark and print the report.

    Parameters
    ----------
    export_type:
        One of 'csv', 'json', 'report'.
    limit:
        Number of top candidates to export.
    n_candidates:
        Total synthetic candidate pool size.
    """
    from app.modules.export.validator import SubmissionValidator
    from app.modules.export.csv_exporter import CSVExporter
    from app.modules.export.json_exporter import JSONExporter
    from app.modules.export.report_exporter import ReportExporter

    print(f"\n{'=' * 60}")
    print(f"  AURA AI — Export Benchmark")
    print(f"  Type: {export_type.upper()}  |  Limit: {limit}  |  Pool: {n_candidates:,}")
    print(f"{'=' * 60}")

    # 1. Generate synthetic data
    t0 = time.perf_counter()
    profiles = _generate_synthetic_profiles(n_candidates)
    details_map = _fake_details_map(profiles)
    t_gen = time.perf_counter() - t0
    print(f"  Data generation : {t_gen * 1000:.1f} ms")

    # 2. Validate
    t1 = time.perf_counter()
    validated = SubmissionValidator.validate(
        profiles, limit=limit, candidate_details_map=details_map
    )
    t_val = time.perf_counter() - t1
    print(f"  Validation      : {t_val * 1000:.1f} ms  ({len(validated)} candidates)")

    # 3. Export
    t2 = time.perf_counter()
    if export_type == "csv":
        content, checksum = CSVExporter.export(validated)
    elif export_type == "json":
        content, checksum = JSONExporter.export(validated, "benchmark")
    elif export_type == "report":
        content, checksum = ReportExporter.export(validated, None, "benchmark")
    else:
        raise ValueError(f"Unknown export_type: {export_type}")
    t_exp = time.perf_counter() - t2
    size_kb = len(content.encode("utf-8")) / 1024

    print(f"  Export          : {t_exp * 1000:.1f} ms")
    print(f"  File size       : {size_kb:.1f} KB")
    print(f"  Checksum (head) : {checksum[:16]}...")

    total_ms = (t_val + t_exp) * 1000
    status_icon = "✅" if total_ms < 2000 else "❌"
    print(f"\n  Total (val+exp) : {total_ms:.1f} ms  {status_icon}  (target < 2,000 ms)")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AURA AI Export Benchmark")
    parser.add_argument("--type", default="csv", choices=["csv", "json", "report"])
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--candidates", type=int, default=100_000)
    args = parser.parse_args()
    run_benchmark(export_type=args.type, limit=args.limit, n_candidates=args.candidates)
