import re

def clean_text(text: str) -> str:
    """Clean up spacing, remove redundant line endings, and normalize formatting characters."""
    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Standardize carriage returns
    text = text.replace("\r", "")
    # Remove consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
