"""
CSV Exporter for the Hack2Skill submission format.

Generates a deterministically ordered, UTF-8 CSV artifact from a validated
list of ranked candidates. Always sorts by rank ascending (rank column
already set by the validator).

Performance target: top‑100 export from 100 000 candidates < 2 seconds total
(validation + CSV generation).
"""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List

from app.modules.export.utils import CSV_COLUMNS, compute_checksum


class CSVExporter:
    """Generates the official Hack2Skill submission CSV."""

    # Column headers exactly as they will appear in the CSV file.
    HEADERS = CSV_COLUMNS

    @classmethod
    def export(cls, candidates: List[Dict[str, Any]]) -> tuple[str, str]:
        """
        Serialize *candidates* to a CSV string.

        Parameters
        ----------
        candidates:
            Validated, rank-annotated candidate dicts (from SubmissionValidator).

        Returns
        -------
        tuple[str, str]
            (csv_content, sha256_checksum)
        """
        buf = io.StringIO()
        writer = csv.DictWriter(
            buf,
            fieldnames=cls.HEADERS,
            extrasaction="ignore",  # ignore keys not in HEADERS
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(candidates)

        csv_content = buf.getvalue()
        checksum = compute_checksum(csv_content)
        return csv_content, checksum

    @classmethod
    def filename(cls, limit: int, profile: str) -> str:
        """Return the canonical submission filename."""
        return f"aura_submission_top{limit}_{profile}.csv"
