from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

class RankingRequest(BaseModel):
    profile: str = Field(default="generic", description="Weight profile to use for ranking")

class RankingEntry(BaseModel):
    candidate_id: str = Field(..., description="Unique candidate identifier")
    overall_score: float = Field(..., description="Aggregated overall score (0-100)")
    semantic_score: float = Field(..., description="Semantic matching score")
    skill_score: float = Field(..., description="Skill match score")
    experience_score: float = Field(..., description="Experience score")
    education_score: float = Field(..., description="Education score")
    certification_score: float = Field(..., description="Certification score")
    language_score: float = Field(..., description="Language score")
    behavior_score: float = Field(..., description="Behavior score")
    decision: Optional[str] = Field(None, description="Hiring decision")
    confidence: Optional[float] = Field(None, description="Decision confidence")
    recommendation: Optional[str] = Field(None, description="Hiring recommendation summary")
