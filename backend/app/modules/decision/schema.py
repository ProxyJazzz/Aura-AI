from pydantic import BaseModel, Field
from typing import List, Optional

class DecisionRequest(BaseModel):
    profile: str = Field(default="generic", description="Weight profile to use for decision making")

class DecisionProfileSchema(BaseModel):
    candidate_id: str = Field(..., description="Unique candidate identifier")
    profile: str = Field(..., description="Weight profile used")
    rank: int = Field(..., description="Candidate rank (1-indexed)")
    overall_score: float = Field(..., description="Aggregated overall score (0-100)")
    recommendation: str = Field(..., description="Hiring recommendation")
    confidence: float = Field(..., description="Decision confidence (0-1)")
    risk_level: str = Field(..., description="Risk level: Low, Medium, High")
    reason_codes: List[str] = Field(default_factory=list, description="Reason codes for the decision")
    strengths: List[str] = Field(default_factory=list, description="Candidate strengths")
    gaps: List[str] = Field(default_factory=list, description="Candidate gaps")
    next_action: str = Field(..., description="Next suggested action for recruiter")
