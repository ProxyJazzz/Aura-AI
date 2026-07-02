from datetime import date
from typing import Optional

def format_date_safe(date_val: Optional[date]) -> Optional[str]:
    """Safely format date object to ISO-8601 string."""
    if date_val is None:
        return None
    return date_val.isoformat()

def anonymize_text(text: str) -> str:
    """Anonymize sensitive text fields by mapping or masking."""
    if not text:
        return "Anonymized"
    parts = text.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}. {parts[1]}"
    return text
