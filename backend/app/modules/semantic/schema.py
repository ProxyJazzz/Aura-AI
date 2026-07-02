from typing import List, Optional
from pydantic import BaseModel, Field

class SemanticStatusResponse(BaseModel):
    """Pydantic model representing the status and size of the semantic cache."""
    is_built: bool = Field(..., description="Flag indicating if the candidate embedding cache is loaded and active")
    total_embeddings: int = Field(..., description="Number of candidate profiles successfully cached")
    cache_file_size_mb: float = Field(..., description="File size of the cached vectors on disk (in MB)")
    last_modified: Optional[str] = Field(None, description="Timestamp of when the cache was last built/modified")
    model_name: str = Field("all-MiniLM-L6-v2", description="Name of the SentenceTransformer model used")
    model_load_time_ms: float = Field(0.0, description="Model load latency in milliseconds")
    last_embedding_time_ms: float = Field(0.0, description="Last batch embedding execution latency in milliseconds")
    memory_usage_mb: float = Field(0.0, description="RAM consumption of the python process in MB")

class TopCandidate(BaseModel):
    """Pydantic model representing a single ranked candidate match."""
    candidate_id: str = Field(..., description="Unique ID of the candidate profile")
    name: str = Field(..., description="Anonymized candidate name")
    title: str = Field(..., description="Current title or role of the candidate")
    score: float = Field(..., description="Normalized semantic score in the range [0.0, 100.0]")
    experience: float = Field(..., description="Years of professional experience")
    location: str = Field(..., description="Location of the candidate")
    skills: List[str] = Field(default_factory=list, description="Extracted candidate skills list")

class SemanticTopResponse(BaseModel):
    """Pydantic model representing the ranked semantic search response."""
    job_id: str = Field(..., description="Unique ID of the active job description")
    job_title: str = Field(..., description="Title of the active job description")
    matches: List[TopCandidate] = Field(..., description="Ranked list of top candidates matching the JD")
    limit: int = Field(..., description="Number of results requested")
    elapsed_ms: float = Field(..., description="Time taken to run retrieval and matrix similarities in milliseconds")
    model_load_time_ms: float = Field(..., description="Lazy model loading duration in milliseconds")
    similarity_time_ms: float = Field(..., description="Matrix cosine similarity lookup duration in milliseconds")
    memory_usage_mb: float = Field(..., description="RAM consumption of the python process in MB")
