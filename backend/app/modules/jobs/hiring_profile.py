from typing import Dict, Any
from app.modules.jobs.section_detector import JobSectionDetector
from app.modules.jobs.metadata_extractor import JobMetadataExtractor
from app.modules.jobs.requirement_classifier import JobRequirementClassifier


class HiringProfileGenerator:
    """Generates the unified structured HiringProfile payload from raw parsed text."""

    @classmethod
    def generate(cls, raw_text: str, upload_info: Dict[str, Any]) -> Dict[str, Any]:
        sections = JobSectionDetector.detect_sections(raw_text)
        metadata = JobMetadataExtractor.extract_metadata(raw_text)
        requirements = JobRequirementClassifier.classify_requirements(sections)

        return {
            "raw_text": raw_text,
            "sections": sections,
            "metadata": metadata,
            "requirements": requirements,
            "upload_metadata": upload_info
        }
