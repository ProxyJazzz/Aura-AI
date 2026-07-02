from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Seniority(str, Enum):
    ENTRY = "Entry"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    PRINCIPAL = "Principal"

class EmploymentType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    FREELANCE = "Freelance"
    INTERNSHIP = "Internship"

class JobModel(BaseModel):
    """Pydantic model representing structured job description features."""
    title: str = Field(..., description="Job Title")
    required_skills: List[str] = Field(default_factory=list, description="Required skills list")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills/nice-to-haves")
    min_experience: float = Field(0.0, description="Minimum experience years required")
    seniority: Seniority = Field(Seniority.SENIOR, description="Seniority level")
    industry: str = Field("Technology", description="Industry/Domain")
    employment_type: EmploymentType = Field(EmploymentType.FULL_TIME, description="Employment type")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills list")

class JobResponse(BaseModel):
    """Pydantic schema returned by APIs containing metadata and parse timestamp."""
    id: str
    title: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience: float
    seniority: Seniority
    industry: str
    employment_type: EmploymentType
    soft_skills: List[str]
    created_at: str
    is_active: bool
