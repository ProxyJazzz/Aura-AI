import hashlib
from typing import Dict, Any
from app.modules.jobs.exceptions import FileValidationError

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

class JobUploadService:
    """Handles uploaded file validations: size, type, corruption, and duplicates."""

    @staticmethod
    def validate_file(filename: str, content: bytes) -> Dict[str, Any]:
        # 1. Validate File Size
        if len(content) == 0:
            raise FileValidationError("File is empty.")
        if len(content) > MAX_FILE_SIZE:
            raise FileValidationError(f"File exceeds maximum size of {MAX_FILE_SIZE / (1024 * 1024)}MB.")

        # 2. Validate File Type
        ext = filename.lower().split('.')[-1]
        if ext not in ['docx', 'txt']:
            raise FileValidationError(f"Unsupported file format: {ext}. Only .docx and .txt are supported.")

        # 3. Check Corrupted DOCX
        if ext == 'docx':
            import zipfile
            import io
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as z:
                    z.read('word/document.xml')
            except Exception as e:
                raise FileValidationError(f"The uploaded DOCX file is corrupted: {str(e)}")

        # 4. Calculate Checksum to help detect duplicates
        sha256 = hashlib.sha256(content).hexdigest()

        return {
            "filename": filename,
            "file_size": len(content),
            "content_type": "text/plain" if ext == 'txt' else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "checksum": sha256
        }
