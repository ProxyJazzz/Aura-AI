from typing import Dict, Any, Tuple, Optional, Set
from pydantic import ValidationError as PydanticValidationError

from app.modules.candidates.schema import CandidateModel
from app.modules.candidates.exceptions import ValidationError

class CandidateValidator:
    """Validates schemas, duplicate IDs, missing fields, and nested structures."""

    def __init__(self):
        self._seen_ids: Set[str] = set()

    def validate_record(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[CandidateModel]]:
        """Validate candidate dictionary against Pydantic CandidateModel and checks duplicates."""
        cid = data.get("candidate_id")
        if not cid:
            return False, "Missing candidate_id", None

        if cid in self._seen_ids:
            return False, f"Duplicate candidate_id: {cid}", None

        self._seen_ids.add(cid)

        try:
            model = CandidateModel(**data)
            return True, None, model
        except PydanticValidationError as e:
            errors = []
            for err in e.errors():
                loc = " -> ".join(str(l) for l in err["loc"])
                msg = err["msg"]
                errors.append(f"[{loc}]: {msg}")
            error_str = " | ".join(errors)
            return False, error_str, None
        except Exception as e:
            return False, f"Unexpected validation error: {str(e)}", None

    def reset(self) -> None:
        """Reset the duplicate ID tracking set."""
        self._seen_ids.clear()
