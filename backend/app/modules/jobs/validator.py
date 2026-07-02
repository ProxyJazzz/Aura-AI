from typing import Dict, Any, Tuple, Optional
from pydantic import ValidationError as PydanticValidationError

from app.modules.jobs.schema import JobModel
from app.modules.jobs.upload import JobUploadService
from app.modules.jobs.exceptions import FileValidationError


class JobValidator:
    """Orchestrates job file uploads validation and schema checking."""

    @staticmethod
    def validate_upload(filename: str, content: bytes) -> Dict[str, Any]:
        """Perform size, extension, corruption, and checksum calculations on file upload."""
        return JobUploadService.validate_file(filename, content)

    @staticmethod
    def validate_schema(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[JobModel]]:
        """Validate parsed dictionary against Pydantic JobModel."""
        try:
            model = JobModel(**data)
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
            return False, f"Schema validation error: {str(e)}", None
Class = JobValidator
