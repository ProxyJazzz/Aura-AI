from typing import List, Dict, Any, Optional
from loguru import logger

from app.modules.candidates.service import CandidateService
from app.modules.decision.cache import DecisionCache
from app.modules.intelligence.schema import (
    DashboardIntelligence,
    CandidateComparisonResponse,
    SkillGapIntelligence,
    MarketIntelligence,
    PipelineHealth,
    RecruiterInsights,
    ReadinessIntelligence
)
from app.modules.intelligence.exceptions import CandidateNotFoundError

from app.modules.intelligence.talent_pool_engine import TalentPoolEngine
from app.modules.intelligence.skill_gap_engine import SkillGapEngine
from app.modules.intelligence.market_insights_engine import MarketInsightsEngine
from app.modules.intelligence.candidate_compare_engine import CandidateCompareEngine
from app.modules.intelligence.pipeline_health_engine import PipelineHealthEngine
from app.modules.intelligence.hiring_readiness_engine import HiringReadinessEngine
from app.modules.intelligence.recommendation_engine import RecruiterInsightsEngine

class IntelligenceService:
    """Orchestrates high-level intelligence generation."""

    @classmethod
    async def get_dashboard(cls, profile: str = "generic") -> DashboardIntelligence:
        decisions = [d.model_dump() for d in DecisionCache.get_top(profile=profile, limit=1000)]
        return TalentPoolEngine.evaluate(decisions)

    @classmethod
    async def get_pipeline_health(cls, profile: str = "generic") -> PipelineHealth:
        decisions = [d.model_dump() for d in DecisionCache.get_top(profile=profile, limit=1000)]
        return PipelineHealthEngine.evaluate(decisions)

    @classmethod
    async def get_readiness(cls, profile: str = "generic") -> ReadinessIntelligence:
        pool = await cls.get_dashboard(profile)
        pipeline = await cls.get_pipeline_health(profile)
        return HiringReadinessEngine.evaluate(pipeline, pool)

    @classmethod
    async def get_insights(cls, profile: str = "generic") -> RecruiterInsights:
        pool = await cls.get_dashboard(profile)
        pipeline = await cls.get_pipeline_health(profile)
        return RecruiterInsightsEngine.evaluate(pool, pipeline)

    @classmethod
    async def get_skill_gaps(cls) -> SkillGapIntelligence:
        candidates = await CandidateService.list_candidates(limit=1000)
        c_dicts = [c.model_dump() for c in candidates]
        return SkillGapEngine.evaluate(c_dicts)

    @classmethod
    async def get_market(cls) -> MarketIntelligence:
        candidates = await CandidateService.list_candidates(limit=1000)
        c_dicts = [c.model_dump() for c in candidates]
        return MarketInsightsEngine.evaluate(c_dicts)

    @classmethod
    async def compare(cls, c1_id: str, c2_id: str, profile: str = "generic") -> CandidateComparisonResponse:
        c1 = DecisionCache.get_candidate(c1_id, profile)
        c2 = DecisionCache.get_candidate(c2_id, profile)
        
        if not c1:
            raise CandidateNotFoundError(f"Candidate {c1_id} not found in decision cache for profile {profile}")
        if not c2:
            raise CandidateNotFoundError(f"Candidate {c2_id} not found in decision cache for profile {profile}")

        return CandidateCompareEngine.evaluate(c1.model_dump(), c2.model_dump())
