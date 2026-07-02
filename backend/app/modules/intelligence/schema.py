from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DashboardIntelligence(BaseModel):
    total_candidates: int
    strong_hires: int
    avg_score: float
    high_risk_candidates: int

class CandidateCompareData(BaseModel):
    candidate_id: str
    semantic_score: float
    skill_score: float
    experience_score: float
    education_score: float
    overall_score: float
    confidence: float
    recommendation: str
    risk_level: str

class CandidateComparisonResponse(BaseModel):
    candidate1: CandidateCompareData
    candidate2: CandidateCompareData
    winner: str = Field(description="candidate_id of the recommended winner based on score")
    delta_score: float = Field(description="Difference in overall scores")

class SkillGapIntelligence(BaseModel):
    missing_skills: List[str]
    high_demand_skills: List[str]
    skill_coverage: float

class MarketIntelligence(BaseModel):
    top_skills: List[str]
    top_universities: List[str]
    top_companies: List[str]
    top_languages: List[str]

class PipelineHealth(BaseModel):
    pipeline_score: int
    avg_confidence: float
    processing_success_rate: float
    resume_quality_avg: float

class RecruiterInsights(BaseModel):
    summary: List[str]
    action_items: List[str]

class ReadinessIntelligence(BaseModel):
    readiness_percentage: int
    bottlenecks: List[str]
