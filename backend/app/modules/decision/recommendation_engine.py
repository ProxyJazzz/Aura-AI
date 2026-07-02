from app.modules.decision.decision_profile import DecisionProfile

class RecommendationEngine:
    """Determines recommendation and next actions based on overall scores."""

    @classmethod
    def evaluate(cls, profile: DecisionProfile):
        """
        Thresholds configurable.
        - Strong Hire: Overall Score >= 85
        - Hire: Overall Score >= 70
        - Technical Interview: Overall Score >= 60 and Skill Score >= 70
        - Recruiter Review: Overall Score >= 50
        - Reject: Overall Score < 50
        """
        score = profile.overall_score
        skill = profile.skill_score

        if score >= 85:
            profile.recommendation = "Strong Hire"
            profile.next_action = "Fast-track to final interview"
        elif score >= 70:
            profile.recommendation = "Hire"
            profile.next_action = "Schedule standard interview"
        elif score >= 60 and skill >= 70:
            profile.recommendation = "Technical Interview"
            profile.next_action = "Proceed with technical assessment"
        elif score >= 50:
            profile.recommendation = "Recruiter Review"
            profile.next_action = "Manual review required"
        else:
            profile.recommendation = "Reject"
            profile.next_action = "Keep in talent pool"
