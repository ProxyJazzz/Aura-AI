import gzip
import json
from pathlib import Path
from typing import Iterator, Dict, Any, Tuple, List, Optional
from loguru import logger

from app.modules.candidates.schema import CandidateModel
from app.modules.candidates.repository import CandidateRepository
from app.modules.candidates.parser import CandidateParser
from app.modules.candidates.validator import CandidateValidator
from app.modules.candidates.feature_extractor import CandidateFeatureExtractor
from app.modules.candidates.statistics import CandidateStatistics
from app.modules.candidates.search import CandidateSearch
from app.modules.candidates.cache import CandidateCache


class CandidateService:
    """Service handling business logic for candidate data parsing, validation, and analytics."""

    @staticmethod
    def stream_load_jsonl(filepath: Path) -> Iterator[str]:
        """Stream lines from a raw or gzipped JSONL file efficiently."""
        if filepath.suffix.lower() == ".gz":
            with gzip.open(filepath, "rt", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield line
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield line

    @classmethod
    def validate_record(cls, data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[CandidateModel]]:
        """Validate candidate dictionary against Pydantic CandidateModel."""
        validator = CandidateValidator()
        return validator.validate_record(data)

    @classmethod
    def extract_features(cls, candidate: CandidateModel) -> Dict[str, Any]:
        """Extract analytical and behavioral features from a validated candidate profile."""
        return CandidateFeatureExtractor.extract_features(candidate)

    @classmethod
    def detect_honeypot(cls, candidate: CandidateModel) -> bool:
        """Detect subtly impossible or inconsistent profiles (Honeypots)."""
        return CandidateFeatureExtractor.detect_honeypot(candidate)

    @classmethod
    def is_consulting_company(cls, company_name: str) -> bool:
        """Check if a company is a services/consulting company."""
        return CandidateFeatureExtractor.is_consulting_company(company_name)

    @classmethod
    def calculate_global_statistics(cls) -> Dict[str, Any]:
        """Calculate aggregate dataset statistics using SQL queries."""
        return CandidateStatistics.calculate()

    @classmethod
    def search_candidates(
        cls, query: str, limit: int = 20, offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search candidate profiles by keyword query."""
        return CandidateSearch.search(query, limit, offset)

    @classmethod
    def get_valid_candidates(cls) -> List[Dict[str, Any]]:
        """Retrieve all valid candidates from the repository."""
        candidates, _ = CandidateRepository.get_candidates(is_valid=True, limit=100000)
        return candidates

    @classmethod
    def get_candidates_by_ids(cls, candidate_ids: List[str]) -> List[Dict[str, Any]]:
        """Retrieve details for a list of candidate IDs."""
        return CandidateRepository.get_candidates_by_ids(candidate_ids)

    @classmethod
    def get_ingestion_status(cls) -> Dict[str, Any]:
        """Retrieve the current candidates database status."""
        stats = CandidateCache.get_statistics()
        if not stats:
            try:
                stats = cls.calculate_global_statistics()
                CandidateCache.save_statistics(stats)
            except Exception:
                stats = {}

        total = stats.get("total_candidates", 0)
        valid = stats.get("valid_candidates", 0)
        malformed = stats.get("malformed_candidates", 0)
        honeypot = stats.get("honeypot_candidates", 0)

        return {
            "is_ingested": total > 0,
            "total_candidates": total,
            "valid_candidates": valid,
            "malformed_candidates": malformed,
            "honeypot_candidates": honeypot
        }

    @classmethod
    def rebuild_dataset(cls, filepath: Optional[str] = None) -> Dict[str, Any]:
        """Rebuild the candidate database from candidates.jsonl dataset file."""
        if not filepath:
            # Default lookup locations
            backend_root = Path(__file__).resolve().parent.parent.parent.parent
            path_options = [
                backend_root / "datasets" / "candidates.jsonl",
                backend_root / "datasets" / "candidates.jsonl.gz",
                backend_root.parent / "datasets" / "candidates.jsonl",
                backend_root.parent / "datasets" / "candidates.jsonl.gz",
                Path("datasets/candidates.jsonl"),
                Path("datasets/candidates.jsonl.gz")
            ]
            for p in path_options:
                if p.exists():
                    filepath = str(p)
                    break

        if not filepath or not Path(filepath).exists():
            raise FileNotFoundError("Candidates dataset file not found.")

        path = Path(filepath)
        logger.info("Rebuilding candidate database from: {file}", file=path)

        # Clear existing data and statistics
        CandidateRepository.create_tables()
        CandidateCache.clear()

        # Simple manual clear in DB
        from app.shared.database import get_db_connection
        with get_db_connection() as conn:
            conn.execute("DELETE FROM candidates;")

        batch = []
        batch_size = 1000
        total_processed = 0
        valid_count = 0
        malformed_count = 0
        honeypot_count = 0

        validator = CandidateValidator()

        for record in CandidateParser.parse_file(path):
            total_processed += 1
            is_valid, err_msg, candidate = validator.validate_record(record)

            if not is_valid:
                malformed_count += 1
                cid = record.get("candidate_id", f"MALFORMED_RECORD_{total_processed}")
                malformed_record = {
                    "candidate_id": cid,
                    "is_valid": 0,
                    "is_honeypot": 0,
                    "validation_error": err_msg,
                    "raw_json": json.dumps(record)
                }
                batch.append(malformed_record)
            else:
                valid_count += 1
                features = CandidateFeatureExtractor.extract_features(candidate)
                if features["is_honeypot"]:
                    honeypot_count += 1
                batch.append(features)

            if len(batch) >= batch_size:
                CandidateRepository.insert_candidates_batch(batch)
                batch = []

        if batch:
            CandidateRepository.insert_candidates_batch(batch)

        logger.info("Computing and saving statistics cache...")
        stats = cls.calculate_global_statistics()
        CandidateCache.save_statistics(stats)

        return {
            "total_processed": total_processed,
            "valid_candidates": valid_count,
            "malformed_candidates": malformed_count,
            "honeypot_candidates": honeypot_count
        }
