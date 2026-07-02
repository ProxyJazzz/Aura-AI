import json
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.core.main import app
from app.modules.jobs.schema import Seniority
from app.modules.features.schema import FeatureProfile
from app.modules.features.skill_engine import SkillEngine
from app.modules.features.experience_engine import ExperienceEngine
from app.modules.features.education_engine import EducationEngine
from app.modules.features.certification_engine import CertificationEngine
from app.modules.features.language_engine import LanguageEngine
from app.modules.features.behavior_engine import BehaviorEngine
from app.modules.features.cache_service import FeatureCacheService
from app.modules.features.service import FeatureService

client = TestClient(app)

# Mock Job payload
MOCK_JOB = {
    "id": "JOB_TEST001",
    "title": "Senior AI Architect",
    "required_skills": ["Python", "PyTorch"],
    "preferred_skills": ["Docker"],
    "min_experience": 5.0,
    "seniority": Seniority.SENIOR,
    "industry": "Technology",
    "soft_skills": ["Leadership"],
    "raw_text": "Looking for a Python/PyTorch specialist.",
    "is_active": True
}

# Mock Candidate payload
MOCK_CANDIDATE = {
    "candidate_id": "CAND_0000001",
    "current_title": "AI Architect",
    "years_of_experience": 6.5,
    "skills_list": "Python, PyTorch, Docker, Git",
    "highest_education_tier": "tier_1",
    "has_masters_or_phd": True,
    "open_to_work_flag": True,
    "avg_tenure_months": 25.0,
    "recruiter_response_rate": 0.9,
    "avg_response_time_hours": 1.5,
    "raw_json": json.dumps({
        "profile": {
            "headline": "Lead AI Engineer",
            "summary": "Building search engines."
        },
        "career_history": [
            {
                "company": "Redrob",
                "title": "Lead AI Engineer",
                "description": "Shipped machine learning platforms."
            }
        ],
        "education": [
            {
                "degree": "Ph.D.",
                "field_of_study": "Computer Science (Research)",
                "institution": "IIT Delhi"
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon",
                "year": 2024
            }
        ],
        "languages": [
            {
                "language": "English",
                "proficiency": "native"
            }
        ]
    })
}

# ── 1. Engine Unit Tests ──────────────────────────────────────────

def test_skill_engine():
    engine = SkillEngine()
    score, meta = engine.calculate(MOCK_CANDIDATE, MOCK_JOB)
    assert score == pytest.approx(100.0) # Matches required [Python, PyTorch] and preferred [Docker]
    assert "coverage" in meta
    assert meta["coverage"] == 100.0
    assert "Git" in meta["additional_skills"]

def test_experience_engine():
    engine = ExperienceEngine()
    score, meta = engine.calculate(MOCK_CANDIDATE, MOCK_JOB)
    # Candidate exp (6.5) > Job min (5.0) -> full points for experience
    # Title overlaps ("AI Architect" vs "Senior AI Architect") -> role points
    # Leadership keyword "lead" in title -> leadership points
    assert score > 70.0
    assert "years_of_experience" in meta

def test_education_engine():
    engine = EducationEngine()
    score, meta = engine.calculate(MOCK_CANDIDATE, MOCK_JOB)
    assert score == pytest.approx(100.0) # Tier 1 (50) + PhD (25) + STEM CS (15) + Research (10)
    assert meta["highest_tier"] == "TIER_1"
    assert meta["is_phd_holder"] is True
    assert meta["is_stem_aligned"] is True

def test_certification_engine():
    engine = CertificationEngine()
    score, meta = engine.calculate(MOCK_CANDIDATE, MOCK_JOB)
    assert score == 30.0 # 1 certification (25) + 1 category (5)
    assert "Cloud" in meta["categories_matched"]

def test_language_engine():
    engine = LanguageEngine()
    score, meta = engine.calculate(MOCK_CANDIDATE, MOCK_JOB)
    # Candidate skills contain: Python (programming language) -> 20 pts
    # Candidate languages contain: English (Native) -> 25 pts
    # Total = 45 points
    assert score == pytest.approx(45.0)
    assert "python" in meta["programming_languages_matched"]

def test_behavior_engine():
    engine = BehaviorEngine()
    score, meta = engine.calculate(MOCK_CANDIDATE, MOCK_JOB)
    # Open to work -> 25 pts
    # avg_tenure (25.0) >= 24 -> 25 pts
    # response_rate (0.9) * 25 -> 22.5 pts
    # response_time (1.5) <= 2.0 -> 25 pts
    # Total = 97.5 points
    assert score == pytest.approx(97.5)

# ── 2. Cache Persistence Unit Tests ──────────────────────────────

def test_features_disk_cache():
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)
    
    mock_profiles = {
        "CAND_0000001": {
            "candidate_id": "CAND_0000001",
            "semantic_score": 85.0,
            "skill_score": 90.0,
            "experience_score": 80.0,
            "education_score": 75.0,
            "certification_score": 60.0,
            "language_score": 90.0,
            "behavior_score": 95.0,
            "feature_vector": [85.0, 90.0, 80.0, 75.0, 60.0, 90.0, 95.0],
            "metadata": {}
        }
    }
    
    with patch.object(FeatureCacheService, 'get_backend_root', return_value=temp_path):
        # 1. Check status empty
        status = FeatureCacheService.get_cache_status()
        assert status["is_built"] is False
        
        # 2. Save cache
        FeatureCacheService.save_cache(mock_profiles)
        
        # 3. Check status built
        status = FeatureCacheService.get_cache_status()
        assert status["is_built"] is True
        assert status["total_profiles"] == 1
        assert status["cache_file_size_mb"] >= 0.0
        
        # 4. Load cache
        loaded = FeatureCacheService.load_cache()
        assert "CAND_0000001" in loaded
        assert loaded["CAND_0000001"]["semantic_score"] == 85.0
        
        # 5. Clear cache
        FeatureCacheService.clear_cache()
        status = FeatureCacheService.get_cache_status()
        assert status["is_built"] is False
        
    temp_dir.cleanup()

# ── 3. Endpoint & Integration Unit Tests ─────────────────────────

def test_features_rest_endpoints():
    # 1. Clear database cache files first
    client.delete("/api/v1/features/cache")
    
    response = client.get("/api/v1/features/status")
    assert response.status_code == 200
    assert response.json()["is_built"] is False
    
    # 2. Match Top Candidates should fail with 400 when cache is empty
    response = client.get("/api/v1/features/top")
    assert response.status_code == 400
    
    # 3. Simulate cache builder.
    # To run instantly, we mock JobService, CandidateService, and SemanticService
    mock_candidates_list = [MOCK_CANDIDATE]
    mock_semantic_results = {
        "job_id": "JOB_TEST001",
        "job_title": "Senior AI Architect",
        "matches": [
            {
                "candidate_id": "CAND_0000001",
                "name": "Anonymized Candidate",
                "title": "AI Architect",
                "score": 88.5
            }
        ]
    }
    
    with patch('app.modules.jobs.service.JobService.get_active_job', return_value=MOCK_JOB):
        with patch('app.modules.candidates.service.CandidateService.get_valid_candidates', return_value=mock_candidates_list):
            with patch('app.modules.semantic.service.SemanticService.get_top_candidates', return_value=mock_semantic_results):
                # Synchronous build call
                FeatureService.build_feature_profiles_cache()
                
    # 4. Check status is built
    response = client.get("/api/v1/features/status")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["is_built"] is True
    assert status_data["total_profiles"] == 1
    
    # 5. Retrieve candidate features scorecard profile
    response = client.get("/api/v1/features/CAND_0000001")
    assert response.status_code == 200
    profile_data = response.json()
    assert profile_data["candidate_id"] == "CAND_0000001"
    assert profile_data["semantic_score"] == 88.5
    assert profile_data["skill_score"] == 100.0
    assert len(profile_data["feature_vector"]) == 7
    
    # 6. Retrieve top categories candidates
    # Mock candidates batch detail query
    mock_candidate_details = [
        {
            "candidate_id": "CAND_0000001",
            "anonymized_name": "Anonymized Candidate",
            "current_title": "AI Architect",
            "skills_list": "Python, PyTorch",
            "years_of_experience": 6.5
        }
    ]
    
    with patch('app.modules.jobs.service.JobService.get_active_job', return_value=MOCK_JOB):
        with patch('app.modules.candidates.service.CandidateService.get_candidates_by_ids', return_value=mock_candidate_details):
            response = client.get("/api/v1/features/top?limit=5")
            assert response.status_code == 200
            top_data = response.json()
            assert top_data["job_id"] == "JOB_TEST001"
            assert len(top_data["skills"]) == 1
            assert top_data["skills"][0]["score"] == 100.0
            
    # Clean up test cache files
    client.delete("/api/v1/features/cache")
