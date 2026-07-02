from typing import List, Dict, Any
from app.modules.intelligence.schema import PipelineHealth

class PipelineHealthEngine:
    """Calculates the health of the candidate ingestion pipeline."""

    @classmethod
    def evaluate(cls, decisions: List[Dict[str, Any]]) -> PipelineHealth:
        if not decisions:
            return PipelineHealth(
                pipeline_score=0,
                avg_confidence=0.0,
                processing_success_rate=0.0,
                resume_quality_avg=0.0
            )

        total = len(decisions)
        avg_confidence = sum(d.get("confidence", 0) for d in decisions) / total
        
        # Simulating resume quality based on semantic score presence and extraction completeness
        # We can use semantic score as a proxy for how well the resume matched standard parsing
        avg_semantic = sum(d.get("semantic_score", 0) for d in decisions) / total

        # Simulated success rate based on candidates that successfully passed decision engine vs total
        # In this context, decisions passed is 100% since they exist in the list.
        success_rate = 100.0

        score = (avg_confidence * 100 * 0.4) + (avg_semantic * 0.4) + (success_rate * 0.2)

        return PipelineHealth(
            pipeline_score=int(score),
            avg_confidence=round(avg_confidence, 2),
            processing_success_rate=success_rate,
            resume_quality_avg=round(avg_semantic, 2)
        )
