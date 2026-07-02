import pytest
from app.modules.intelligence.talent_pool_engine import TalentPoolEngine
from app.modules.intelligence.skill_gap_engine import SkillGapEngine
from app.modules.intelligence.candidate_compare_engine import CandidateCompareEngine
from app.modules.intelligence.pipeline_health_engine import PipelineHealthEngine
from app.modules.intelligence.hiring_readiness_engine import HiringReadinessEngine
from app.modules.intelligence.market_insights_engine import MarketInsightsEngine
from app.modules.intelligence.recommendation_engine import RecruiterInsightsEngine

def test_talent_pool_engine():
    decisions = [
        {"recommendation": "Strong Hire", "overall_score": 90, "risk_level": "Low"},
        {"recommendation": "Hire", "overall_score": 75, "risk_level": "Low"},
        {"recommendation": "Reject", "overall_score": 40, "risk_level": "High"}
    ]
    res = TalentPoolEngine.evaluate(decisions)
    assert res.total_candidates == 3
    assert res.strong_hires == 1
    assert res.high_risk_candidates == 1
    assert res.avg_score == pytest.approx(68.33, 0.1)

def test_skill_gap_engine():
    candidates = [
        {"skills": '[{"name": "Python"}, {"name": "React"}]'},
        {"skills": '[{"name": "Python"}, {"name": "Docker"}]'},
    ]
    res = SkillGapEngine.evaluate(candidates)
    assert "Python" in res.high_demand_skills
    assert "React" in res.missing_skills or "Docker" in res.missing_skills
    assert res.skill_coverage > 0

def test_candidate_compare_engine():
    c1 = {"candidate_id": "c1", "overall_score": 85, "semantic_score": 90}
    c2 = {"candidate_id": "c2", "overall_score": 70, "semantic_score": 60}
    res = CandidateCompareEngine.evaluate(c1, c2)
    assert res.winner == "c1"
    assert res.delta_score == 15.0

def test_pipeline_health_engine():
    decisions = [
        {"confidence": 0.8, "semantic_score": 90},
        {"confidence": 0.6, "semantic_score": 70}
    ]
    res = PipelineHealthEngine.evaluate(decisions)
    assert res.avg_confidence == pytest.approx(0.7)
    assert res.resume_quality_avg == pytest.approx(80.0)
    assert res.processing_success_rate == 100.0

def test_market_insights_engine():
    candidates = [
        {"experience": '[{"company": "Google"}]', "education": '[{"institution": "MIT"}]'}
    ]
    res = MarketInsightsEngine.evaluate(candidates)
    assert "Google" in res.top_companies
    assert "MIT" in res.top_universities

def test_hiring_readiness_engine():
    pool = TalentPoolEngine.evaluate([
        {"recommendation": "Strong Hire", "overall_score": 90, "risk_level": "Low"}
    ])
    pipeline = PipelineHealthEngine.evaluate([
        {"confidence": 0.9, "semantic_score": 90}
    ])
    # Pool size < 10 will trigger a bottleneck (-20)
    res = HiringReadinessEngine.evaluate(pipeline, pool)
    assert "Low candidate volume" in res.bottlenecks
    assert res.readiness_percentage == 80

def test_recruiter_insights_engine():
    pool = TalentPoolEngine.evaluate([
        {"recommendation": "Strong Hire", "overall_score": 90, "risk_level": "Low"}
    ])
    pipeline = PipelineHealthEngine.evaluate([
        {"confidence": 0.9, "semantic_score": 90}
    ])
    res = RecruiterInsightsEngine.evaluate(pool, pipeline)
    assert len(res.summary) > 0
    assert len(res.action_items) > 0
