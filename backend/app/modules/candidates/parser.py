import gzip
import json
from pathlib import Path
from typing import Iterator, Dict, Any
from app.modules.candidates.exceptions import ParseError

class CandidateParser:
    """Streams JSONL datasets and parses candidates records without validating."""

    @staticmethod
    def parse_file(filepath: Path) -> Iterator[Dict[str, Any]]:
        """Efficiently stream and parse candidate records from a raw or gzipped JSONL file."""
        if not filepath.exists():
            raise ParseError(f"Dataset file not found at {filepath}")

        try:
            if filepath.suffix.lower() == ".gz":
                with gzip.open(filepath, "rt", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            yield json.loads(line)
            else:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            yield json.loads(line)
        except Exception as e:
            raise ParseError(f"Failed to stream and parse file {filepath}: {str(e)}")
