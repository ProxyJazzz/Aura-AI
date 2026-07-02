import pytest
import os
import shutil
from unittest.mock import patch, MagicMock

from app.modules.ranking.weight_engine import WeightEngine
from app.modules.ranking.normalization_engine import NormalizationEngine
from app.modules.ranking.aggregation_engine import AggregationEngine
from app.modules.ranking.confidence_engine import ConfidenceEngine
from app.modules.ranking.ranking_engine import RankingEngine
from app.modules.ranking.configuration import RankingEntry
from app.modules.ranking.exceptions import InvalidWeightProfileError

def test_weight_engine_default():
    weights = WeightEngine.load_weights("nonexistent_profile")
    assert weights["semantic"] == 25.0
    assert weights["skills"] == 20.0
    assert sum(weights.values()) == 100.0

def test_normalization_engine():
    assert NormalizationEngine.normalize(150.0) == 100.0
    assert NormalizationEngine.normalize(-10.0) == 0.0
    assert NormalizationEngine.normalize(85.556) == 85.56

def test_aggregation_engine():
    features = {
        "semantic_score": 80.0,
        "skill_score": 90.0,
        "experience_score": 70.0,
        "education_score": 60.0,
        "certification_score": 50.0,
        "language_score": 40.0,
        "behavior_score": 30.0
    }
    weights = WeightEngine.DEFAULT_WEIGHTS
    
    # Calculation manually:
    # 80*0.25 + 90*0.20 + 70*0.15 + 60*0.10 + 50*0.10 + 40*0.10 + 30*0.10
    # = 20 + 18 + 10.5 + 6 + 5 + 4 + 3 = 66.5
    score = AggregationEngine.compute_overall_score(features, weights)
    assert score == 66.5

def test_confidence_engine():
    decision, conf, rec = ConfidenceEngine.evaluate(90.0)
    assert decision == "STRONG_YES"
    assert conf == 0.90
    assert "immediate interview" in rec

    decision, conf, rec = ConfidenceEngine.evaluate(75.0)
    assert decision == "YES"
    assert conf == 0.75

    decision, conf, rec = ConfidenceEngine.evaluate(60.0)
    assert decision == "MAYBE"
    assert conf == 0.65

    decision, conf, rec = ConfidenceEngine.evaluate(40.0)
    assert decision == "NO"
    assert conf == 0.60

def test_ranking_engine_sort():
    c1 = RankingEntry(candidate_id="C1", overall_score=80.0, semantic_score=70.0, skill_score=60.0, experience_score=50.0, education_score=0, certification_score=0, language_score=0, behavior_score=0)
    c2 = RankingEntry(candidate_id="C2", overall_score=80.0, semantic_score=80.0, skill_score=60.0, experience_score=50.0, education_score=0, certification_score=0, language_score=0, behavior_score=0)
    c3 = RankingEntry(candidate_id="C3", overall_score=90.0, semantic_score=70.0, skill_score=60.0, experience_score=50.0, education_score=0, certification_score=0, language_score=0, behavior_score=0)
    
    ranked = RankingEngine.rank([c1, c2, c3])
    
    assert ranked[0].candidate_id == "C3" # Highest overall
    assert ranked[1].candidate_id == "C2" # Tie breaker semantic
    assert ranked[2].candidate_id == "C1"
