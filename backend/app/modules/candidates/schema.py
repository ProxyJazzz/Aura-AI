from datetime import date
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator

# ── Enums ────────────────────────────────────────────────────────

class CompanySize(str, Enum):
    SIZE_1_10 = "1-10"
    SIZE_11_50 = "11-50"
    SIZE_51_200 = "51-200"
    SIZE_201_500 = "201-500"
    SIZE_501_1000 = "501-1000"
    SIZE_1001_5000 = "1001-5000"
    SIZE_5001_10000 = "5001-10000"
    SIZE_10001_PLUS = "10001+"

class EducationTier(str, Enum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    TIER_4 = "tier_4"
    UNKNOWN = "unknown"

class SkillProficiency(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LanguageProficiency(str, Enum):
    BASIC = "basic"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    NATIVE = "native"

class PreferredWorkMode(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    FLEXIBLE = "flexible"

# ── Models ───────────────────────────────────────────────────────

class ProfileModel(BaseModel):
    anonymized_name: str = Field(description="Anonymized full name")
    headline: str = Field(description="One-line professional headline")
    summary: str = Field(description="Professional summary")
    location: str = Field(description="City/region")
    country: str = Field(description="Country")
    years_of_experience: float = Field(ge=0, le=50, description="Total years of professional experience")
    current_title: str = Field(description="Current job title")
    current_company: str = Field(description="Current employer")
    current_company_size: CompanySize = Field(description="Size of current company")
    current_industry: str = Field(description="Current industry sector")

class CareerHistoryItem(BaseModel):
    company: str = Field(description="Company name")
    title: str = Field(description="Role title")
    start_date: str = Field(description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD), null if current")
    duration_months: int = Field(ge=0, description="Duration in months")
    is_current: bool = Field(description="Is this the current role?")
    industry: str = Field(description="Industry sector")
    company_size: CompanySize = Field(description="Size of the company")
    description: str = Field(description="Responsibilities and accomplishments")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        try:
            # Check if it parses as date
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Date '{v}' must be in YYYY-MM-DD format")

class EducationItem(BaseModel):
    institution: str = Field(description="Institution name")
    degree: str = Field(description="Degree type")
    field_of_study: str = Field(description="Major or field of study")
    start_year: int = Field(ge=1970, le=2030, description="Year education started")
    end_year: int = Field(ge=1970, le=2035, description="Year education ended")
    grade: Optional[str] = Field(default=None, description="Grade point average, class, or percentage")
    tier: EducationTier = Field(default=EducationTier.UNKNOWN, description="Institution tier")

class SkillItem(BaseModel):
    name: str = Field(description="Skill name")
    proficiency: SkillProficiency = Field(description="Candidate's skill level")
    endorsements: int = Field(ge=0, description="Number of endorsements received")
    duration_months: Optional[int] = Field(default=None, ge=0, description="Months of usage")

class CertificationItem(BaseModel):
    name: str = Field(description="Certification name")
    issuer: str = Field(description="Issuer organization")
    year: int = Field(description="Year issued")

class LanguageItem(BaseModel):
    language: str = Field(description="Language name")
    proficiency: LanguageProficiency = Field(description="Language fluency level")

class ExpectedSalaryRange(BaseModel):
    min: float = Field(ge=0, description="Minimum expected salary in LPA")
    max: float = Field(ge=0, description="Maximum expected salary in LPA")

class RedrobSignals(BaseModel):
    profile_completeness_score: float = Field(ge=0, le=100)
    signup_date: str
    last_active_date: str
    open_to_work_flag: bool
    profile_views_received_30d: int = Field(ge=0)
    applications_submitted_30d: int = Field(ge=0)
    recruiter_response_rate: float = Field(ge=0.0, le=1.0)
    avg_response_time_hours: float = Field(ge=0.0)
    skill_assessment_scores: Dict[str, float] = Field(default_factory=dict)
    connection_count: int = Field(ge=0)
    endorsements_received: int = Field(ge=0)
    notice_period_days: int = Field(ge=0, le=180)
    expected_salary_range_inr_lpa: ExpectedSalaryRange
    preferred_work_mode: PreferredWorkMode
    willing_to_relocate: bool
    github_activity_score: float = Field(ge=-1.0, le=100.0)
    search_appearance_30d: int = Field(ge=0)
    saved_by_recruiters_30d: int = Field(ge=0)
    interview_completion_rate: float = Field(ge=0.0, le=1.0)
    offer_acceptance_rate: float = Field(ge=-1.0, le=1.0)
    verified_email: bool
    verified_phone: bool
    linkedin_connected: bool

    @field_validator("signup_date", "last_active_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Date '{v}' must be in YYYY-MM-DD format")

class CandidateModel(BaseModel):
    candidate_id: str = Field(pattern=r"^CAND_[0-9]{7}$", description="7-digit unique identifier")
    profile: ProfileModel
    career_history: List[CareerHistoryItem] = Field(min_length=1, max_length=10)
    education: List[EducationItem] = Field(default_factory=list, max_length=5)
    skills: List[SkillItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    languages: List[LanguageItem] = Field(default_factory=list)
    redrob_signals: RedrobSignals

# ── API Response Models ──────────────────────────────────────────

class CandidateDetailResponse(BaseModel):
    """API response schema for a single candidate, containing raw data and features."""
    candidate_id: str
    is_valid: bool
    is_honeypot: bool
    validation_error: Optional[str] = None
    data: Optional[CandidateModel] = None  # Valid candidate details
    raw_json: str  # Original JSON string
    
    # Extracted Features Summary
    features: Dict[str, Any]

class CandidateListResponse(BaseModel):
    """API response schema for a list of candidates."""
    items: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int

class DatasetSummaryResponse(BaseModel):
    """API response schema for global dataset statistics."""
    total_candidates: int
    valid_candidates: int
    malformed_candidates: int
    honeypot_candidates: int
    experience_distribution: Dict[str, Any]
    education_tier_distribution: Dict[str, int]
    top_skills: List[Dict[str, Any]]
    top_industries: List[Dict[str, Any]]
    open_to_work_percentage: float
    avg_profile_completeness: float
    avg_recruiter_response_rate: float
