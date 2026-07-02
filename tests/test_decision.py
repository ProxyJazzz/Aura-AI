import pytest
from app.modules.decision.decision_profile import DecisionProfile
from app.modules.decision.recommendation_engine import RecommendationEngine
from app.modules.decision.confidence_engine import ConfidenceEngine
from app.modules.decision.risk_engine import RiskEngine
from app.modules.decision.reason_engine import ReasonEngine

def get_base_profile(
    overall=0.0, semantic=0.0, skill=0.0, experience=0.0, 
    education=0.0, cert=0.0, lang=0.0, behavior=0.0
) -> DecisionProfile:
    return DecisionProfile(
        candidate_id="test_candidate",
        profile="generic",
        rank=1,
        overall_score=overall,
        semantic_score=semantic,
        skill_score=skill,
        experience_score=experience,
        education_score=education,
        certification_score=cert,
        language_score=lang,
        behavior_score=behavior
    )

def test_recommendation_engine():
    # Strong Hire
    profile = get_base_profile(overall=86)
    RecommendationEngine.evaluate(profile)
    assert profile.recommendation == "Strong Hire"

    # Hire
    profile = get_base_profile(overall=75)
    RecommendationEngine.evaluate(profile)
    assert profile.recommendation == "Hire"

    # Technical Interview
    profile = get_base_profile(overall=65, skill=75)
    RecommendationEngine.evaluate(profile)
    assert profile.recommendation == "Technical Interview"

    # Recruiter Review (score 65 but skill < 70)
    profile = get_base_profile(overall=65, skill=60)
    RecommendationEngine.evaluate(profile)
    assert profile.recommendation == "Recruiter Review"

    # Reject
    profile = get_base_profile(overall=45)
    RecommendationEngine.evaluate(profile)
    assert profile.recommendation == "Reject"

def test_confidence_engine():
    # All scores 100 -> std_dev 0 -> penalty 0
    profile = get_base_profile(100, 100, 100, 100, 100, 100, 100, 100)
    ConfidenceEngine.evaluate(profile)
    assert profile.confidence == 1.0

    # Half 0 half 100 -> high variance
    profile = get_base_profile(50, 100, 100, 100, 100, 0, 0, 0)
    ConfidenceEngine.evaluate(profile)
    assert profile.confidence < 0.50

def test_risk_engine():
    # Low Risk
    profile = get_base_profile(overall=80, skill=80, experience=80, education=80, behavior=80)
    RiskEngine.evaluate(profile)
    assert profile.risk_level == "Low"
    assert len(profile.gaps) == 0

    # Medium Risk
    profile = get_base_profile(overall=60, skill=80, experience=40, education=40, behavior=80)
    RiskEngine.evaluate(profile)
    assert profile.risk_level == "Medium"
    assert "Experience gap" in profile.gaps

    # High Risk
    profile = get_base_profile(overall=40, skill=40, experience=40, education=40, behavior=40)
    RiskEngine.evaluate(profile)
    assert profile.risk_level == "High"
    
    # Honeypot
    profile = get_base_profile(overall=50, skill=80, experience=80, education=80, behavior=0)
    RiskEngine.evaluate(profile)
    assert profile.risk_level == "High"
    assert "High likelihood honeypot candidate" in profile.gaps

def test_reason_engine():
    profile = get_base_profile(overall=90, semantic=85, skill=85, experience=85, education=85, cert=85, lang=85, behavior=85)
    ReasonEngine.evaluate(profile)
    assert "SEMANTIC_FIT_HIGH" in profile.reason_codes
    assert "SKILL_MATCH" in profile.reason_codes
    assert len(profile.strengths) == 7
