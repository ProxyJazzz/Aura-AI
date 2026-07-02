from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class FeatureProfile(BaseModel):
    """Pydantic model representing a candidate's complete feature intelligence scorecard."""
    candidate_id: str = Field(..., description="Unique 7-digit candidate identifier")
    semantic_score: float = Field(..., description="Cosine similarity score (0-100) from the Semantic Layer")
    skill_score: float = Field(..., description="Weighted score matching required vs preferred skills")
    experience_score: float = Field(..., description="Score evaluating total tenure, career stability, progression, and company prestige")
    education_score: float = Field(..., description="Score evaluating highest degree, fields of study, institution tiers, and PhDs")
    certification_score: float = Field(..., description="Score evaluating cloud, data, ML/AI, security, and devops credentials")
    language_score: float = Field(..., description="Score evaluating programming languages and human language fluencies")
    behavior_score: float = Field(..., description="Score evaluating notice period, availability, and engagement responsiveness")
    feature_vector: List[float] = Field(..., description="Flat vector array representation of all scores for machine learning layers")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic payload including missing skills, experience breakdown, and reasoning")

class FeatureStatusResponse(BaseModel):
    """Pydantic model representing feature cache stats on the filesystem."""
    is_built: bool = Field(..., description="Flag indicating if the candidate features cache is loaded and active")
    total_profiles: int = Field(..., description="Number of candidate feature scorecards cached")
    cache_file_size_mb: float = Field(..., description="File size of the cached profiles JSON on disk (in MB)")
    last_modified: Optional[str] = Field(None, description="Timestamp of when the cache was last written")
    candidates_processed_per_second: float = Field(0.0, description="Throughput metrics during cache generation")

class CategoryTopCandidate(BaseModel):
    """Pydantic model representing a high-scoring candidate in a specific category."""
    candidate_id: str
    name: str
    title: str
    score: float

class FeatureTopResponse(BaseModel):
    """Pydantic model representing top-scoring candidates grouped by category."""
    job_id: str
    job_title: str
    skills: List[CategoryTopCandidate]
    experience: List[CategoryTopCandidate]
    education: List[CategoryTopCandidate]
    behavior: List[CategoryTopCandidate]
