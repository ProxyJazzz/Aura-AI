import re
from typing import Dict

class JobSectionDetector:
    """Detects sections in raw job description text based on keyword headers."""

    SECTION_PATTERNS = {
        "Preferred Qualifications": [
            r"\b(?:preferred qualifications|preferred skills|desired skills|preferred experience|desired qualifications)\b"
        ],
        "Nice To Have": [
            r"\b(?:nice to have|plusses|plus point|good to have|bonus points)\b"
        ],
        "Exclusions": [
            r"\b(?:exclusions|non-goals|out of scope|not required)\b"
        ],
        "Requirements": [
            r"\b(?:requirements|minimum qualifications|what you need|required skills|must have|basic qualifications|qualifications|experience required)\b"
        ],
        "Responsibilities": [
            r"\b(?:responsibilities|key responsibilities|what you will do|what you\'ll do|role details|duties|tasks|responsibilities include)\b"
        ],
        "Summary": [
            r"\b(?:summary|about us|about the company|overview|company overview|description|introduction)\b"
        ],
        "Benefits": [
            r"\b(?:benefits|perks|what we offer|compensation|benefits include|what\'s in it for you)\b"
        ]
    }

    @classmethod
    def detect_sections(cls, text: str) -> Dict[str, str]:
        """Detect and slice sections in the raw job description text."""
        lines = text.split("\n")
        sections = {
            "Summary": "",
            "Responsibilities": "",
            "Requirements": "",
            "Preferred Qualifications": "",
            "Nice To Have": "",
            "Benefits": "",
            "Exclusions": ""
        }
        
        current_section = "Summary"
        section_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                section_lines.append("")
                continue

            # Check if this line looks like a header (short line, matches key patterns)
            is_header = False
            if len(stripped) < 80:
                for section_name, patterns in cls.SECTION_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, stripped.lower()):
                            # Flush current section
                            if section_lines:
                                sections[current_section] = (sections[current_section] + "\n" + "\n".join(section_lines)).strip()
                                section_lines = []
                            current_section = section_name
                            is_header = True
                            break
                    if is_header:
                        break

            if not is_header:
                section_lines.append(stripped)

        if section_lines:
            sections[current_section] = (sections[current_section] + "\n" + "\n".join(section_lines)).strip()

        return sections
