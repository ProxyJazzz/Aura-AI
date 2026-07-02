from app.modules.intelligence.schema import RecruiterInsights, DashboardIntelligence, PipelineHealth

class RecruiterInsightsEngine:
    """Generates deterministic recruiter insights and action items."""

    @classmethod
    def evaluate(cls, pool: DashboardIntelligence, pipeline: PipelineHealth) -> RecruiterInsights:
        summary = []
        action_items = []

        if pool.strong_hires > 0:
            summary.append(f"Identified {pool.strong_hires} strong hire candidates ready for final interviews.")
            action_items.append("Schedule final interviews for Strong Hire candidates.")
        else:
            summary.append("No strong hires identified yet.")
            action_items.append("Consider sourcing more candidates or adjusting job requirements.")

        if pool.high_risk_candidates > 0:
            summary.append(f"Detected {pool.high_risk_candidates} candidates with high risk profiles.")
            action_items.append("Review high risk flags in the candidate explorer before rejecting.")

        if pipeline.avg_confidence < 0.70:
            summary.append("AI confidence is currently low.")
            action_items.append("Provide a more detailed job description to improve semantic matching confidence.")
        else:
            summary.append("High AI confidence in matching algorithms.")

        return RecruiterInsights(
            summary=summary,
            action_items=action_items
        )
