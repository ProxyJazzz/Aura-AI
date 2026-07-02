from app.modules.intelligence.schema import ReadinessIntelligence, PipelineHealth, DashboardIntelligence

class HiringReadinessEngine:
    """Calculates overall readiness to make a hiring decision."""

    @classmethod
    def evaluate(cls, pipeline: PipelineHealth, pool: DashboardIntelligence) -> ReadinessIntelligence:
        bottlenecks = []
        readiness = 100

        if pool.total_candidates < 10:
            bottlenecks.append("Low candidate volume")
            readiness -= 20
        
        if pool.strong_hires == 0:
            bottlenecks.append("No strong hires identified")
            readiness -= 30

        if pipeline.avg_confidence < 0.70:
            bottlenecks.append("Low AI decision confidence")
            readiness -= 15

        if pool.high_risk_candidates > (pool.total_candidates * 0.2):
            bottlenecks.append("High risk candidate pool")
            readiness -= 15

        return ReadinessIntelligence(
            readiness_percentage=max(0, readiness),
            bottlenecks=bottlenecks
        )
