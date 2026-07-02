import json
import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.core.main import app
from app.modules.candidates.schema import CandidateModel, SkillProficiency
from app.modules.candidates.service import CandidateService
from app.modules.candidates.repository import CandidateRepository

client = TestClient(app)

# ── Sample Data for Testing ──────────────────────────────────────

SAMPLE_CANDIDATE = {
    "candidate_id": "CAND_0000001",
    "profile": {
        "anonymized_name": "Ira Vora",
        "headline": "Backend Engineer | SQL, Spark, Cloud",
        "summary": "Software / data professional with 6.9 years of experience.",
        "location": "Toronto",
        "country": "Canada",
        "years_of_experience": 6.9,
        "current_title": "Backend Engineer",
        "current_company": "Mindtree",
        "current_company_size": "10001+",
        "current_industry": "IT Services"
    },
    "career_history": [
        {
            "company": "Mindtree",
            "title": "Backend Engineer",
            "start_date": "2024-03-08",
            "end_date": None,
            "duration_months": 27,
            "is_current": True,
            "industry": "IT Services",
            "company_size": "10001+",
            "description": "Implemented streaming data pipelines."
        }
    ],
    "education": [
        {
            "institution": "Lovely Professional University",
            "degree": "B.E.",
            "field_of_study": "Computer Science",
            "start_year": 2017,
            "end_year": 2020,
            "grade": "8.24 CGPA",
            "tier": "tier_3"
        }
    ],
    "skills": [
        {
            "name": "Python",
            "proficiency": "expert",
            "endorsements": 10,
            "duration_months": 48
        }
    ],
    "certifications": [],
    "languages": [
        {
            "language": "English",
            "proficiency": "professional"
        }
    ],
    "redrob_signals": {
        "profile_completeness_score": 86.9,
        "signup_date": "2025-10-16",
        "last_active_date": "2026-05-20",
        "open_to_work_flag": True,
        "profile_views_received_30d": 23,
        "applications_submitted_30d": 2,
        "recruiter_response_rate": 0.34,
        "avg_response_time_hours": 177.8,
        "skill_assessment_scores": {},
        "connection_count": 356,
        "endorsements_received": 35,
        "notice_period_days": 60,
        "expected_salary_range_inr_lpa": {
            "min": 18.7,
            "max": 36.1
        },
        "preferred_work_mode": "onsite",
        "willing_to_relocate": False,
        "github_activity_score": 9.2,
        "search_appearance_30d": 249,
        "saved_by_recruiters_30d": 4,
        "interview_completion_rate": 0.71,
        "offer_acceptance_rate": 0.58,
        "verified_email": True,
        "verified_phone": True,
        "linkedin_connected": False
    }
}

# ── Service & Validation Tests ───────────────────────────────────

def test_candidate_pydantic_validation():
    # Test valid candidate
    is_valid, err, model = CandidateService.validate_record(SAMPLE_CANDIDATE)
    assert is_valid is True
    assert err is None
    assert model.candidate_id == "CAND_0000001"
    
    # Test invalid candidate (missing profile headline)
    invalid_candidate = SAMPLE_CANDIDATE.copy()
    invalid_candidate["profile"] = SAMPLE_CANDIDATE["profile"].copy()
    del invalid_candidate["profile"]["headline"]
    
    is_valid, err, model = CandidateService.validate_record(invalid_candidate)
    assert is_valid is False
    assert "profile -> headline" in err

def test_honeypot_detection():
    # Test normal candidate
    is_valid, _, candidate = CandidateService.validate_record(SAMPLE_CANDIDATE)
    assert CandidateService.detect_honeypot(candidate) is False
    
    # Test expert skill with 0 duration honeypot
    honeypot_1 = json.loads(json.dumps(SAMPLE_CANDIDATE))
    honeypot_1["skills"].append({
        "name": "Go",
        "proficiency": "expert",
        "endorsements": 5,
        "duration_months": 0
    })
    _, _, cand_hp1 = CandidateService.validate_record(honeypot_1)
    assert CandidateService.detect_honeypot(cand_hp1) is True

    # Test single job exceeds total experience honeypot
    honeypot_2 = json.loads(json.dumps(SAMPLE_CANDIDATE))
    honeypot_2["career_history"][0]["duration_months"] = 100  # total exp is 6.9 yrs = 82.8 months
    _, _, cand_hp2 = CandidateService.validate_record(honeypot_2)
    assert CandidateService.detect_honeypot(cand_hp2) is True

def test_feature_extraction():
    is_valid, _, candidate = CandidateService.validate_record(SAMPLE_CANDIDATE)
    features = CandidateService.extract_features(candidate)
    
    assert features["candidate_id"] == "CAND_0000001"
    assert features["skills_list"] == "Python"
    assert features["has_ai_ml_skills"] == 0  # Python is not an AI/ML specific skill in our list
    assert features["has_worked_in_consulting"] == 1  # Mindtree is a services/consulting firm
    assert features["highest_education_tier"] == "tier_3"
    assert features["has_masters_or_phd"] == 0
    assert features["is_honeypot"] == 0

    # Test with an AI/ML skill
    aiml_candidate = json.loads(json.dumps(SAMPLE_CANDIDATE))
    aiml_candidate["skills"].append({
        "name": "PyTorch",
        "proficiency": "advanced",
        "endorsements": 10,
        "duration_months": 24
    })
    _, _, cand_aiml = CandidateService.validate_record(aiml_candidate)
    features_aiml = CandidateService.extract_features(cand_aiml)
    assert features_aiml["has_ai_ml_skills"] == 1


def test_streaming_loader():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as temp_file:
        temp_file.write(json.dumps(SAMPLE_CANDIDATE) + "\n")
        temp_file_path = Path(temp_file.name)
        
    try:
        lines = list(CandidateService.stream_load_jsonl(temp_file_path))
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["candidate_id"] == "CAND_0000001"
    finally:
        os.unlink(temp_file.name)

# ── API Endpoint Tests ───────────────────────────────────────────

def test_get_dataset_summary():
    response = client.get("/api/v1/dataset/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_candidates" in data
    assert data["total_candidates"] == 100000
    assert data["valid_candidates"] == 100000
    assert data["honeypot_candidates"] == 60

def test_get_candidates_statistics():
    response = client.get("/api/v1/candidates/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "total_candidates" in data
    assert data["total_candidates"] == 100000
    assert data["valid_candidates"] == 100000
    assert data["honeypot_candidates"] == 60

def test_get_candidates_endpoint():
    # Test basic list
    response = client.get("/api/v1/candidates?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 5
    
    # Test filtering by experience
    response = client.get("/api/v1/candidates?min_experience=15.0&limit=5")
    assert response.status_code == 200
    items = response.json()["items"]
    for item in items:
        assert item["years_of_experience"] >= 15.0
        
    # Test filtering by location
    response = client.get("/api/v1/candidates?location=Toronto&limit=5")
    assert response.status_code == 200
    items = response.json()["items"]
    for item in items:
        assert "toronto" in item["location"].lower()

def test_get_candidate_by_id_endpoint():
    # Test valid candidate detail retrieval
    response = client.get("/api/v1/candidates/CAND_0000001")
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_id"] == "CAND_0000001"
    assert data["is_valid"] is True
    assert data["features"]["anonymized_name"] == "Ira Vora"
    
    # Test invalid candidate ID
    response = client.get("/api/v1/candidates/CAND_9999999")
    assert response.status_code == 404


def test_candidates_search_endpoint():
    """Verify that keyword search endpoint returns results."""
    # Seed the DB candidate Iraq Vora
    response = client.get("/api/v1/candidates/search?q=Ira")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    
    # Search for non-existent keyword
    response = client.get("/api/v1/candidates/search?q=NonExistentSkillNameXYZ")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_candidates_status_endpoint():
    """Verify that candidate status returns database status successfully."""
    response = client.get("/api/v1/candidates/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_ingested" in data
    assert "total_candidates" in data


def test_candidate_parser_direct():
    """Verify CandidateParser stream parsing."""
    from app.modules.candidates.parser import CandidateParser
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as temp_file:
        temp_file.write(json.dumps(SAMPLE_CANDIDATE) + "\n")
        temp_file_path = Path(temp_file.name)
        
    try:
        records = list(CandidateParser.parse_file(temp_file_path))
        assert len(records) == 1
        assert records[0]["candidate_id"] == "CAND_0000001"
    finally:
        os.unlink(temp_file.name)


def test_candidate_validator_direct():
    """Verify CandidateValidator schema validation and duplicate checking."""
    from app.modules.candidates.validator import CandidateValidator
    validator = CandidateValidator()
    
    # First validation succeeds
    is_valid, err, model = validator.validate_record(SAMPLE_CANDIDATE)
    assert is_valid is True
    assert err is None
    
    # Duplicate validation fails
    is_valid, err, model = validator.validate_record(SAMPLE_CANDIDATE)
    assert is_valid is False
    assert "Duplicate" in err


def test_candidate_feature_extractor_direct():
    """Verify CandidateFeatureExtractor correctly computes candidate properties."""
    from app.modules.candidates.feature_extractor import CandidateFeatureExtractor
    is_valid, _, candidate = CandidateService.validate_record(SAMPLE_CANDIDATE)
    features = CandidateFeatureExtractor.extract_features(candidate)
    
    assert features["candidate_id"] == "CAND_0000001"
    assert features["skills_list"] == "Python"
    assert features["has_worked_in_consulting"] == 1


def test_candidate_statistics_direct():
    """Verify CandidateStatistics returns computed metrics structure."""
    from app.modules.candidates.statistics import CandidateStatistics
    stats = CandidateStatistics.calculate()
    assert "total_candidates" in stats
    assert "valid_candidates" in stats
    assert "experience_distribution" in stats

