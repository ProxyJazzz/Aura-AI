from app.modules.decision.decision_profile import DecisionProfile

class RiskEngine:
    """Determines Risk (Low/Medium/High) by scanning for gaps and missing criteria."""

    @classmethod
    def evaluate(cls, profile: DecisionProfile):
        """
        Risk Engine criteria:
        - Missing required skills: Skill Score < 50
        - Experience gap: Experience Score < 50
        - Education mismatch: Education Score < 50
        - Career instability: Behavior Score < 50
        - Honeypot candidates: Behavior Score == 0
        """
        risk_flags = 0
        
        if profile.skill_score < 50:
            profile.gaps.append("Missing required skills")
            risk_flags += 2
            
        if profile.experience_score < 50:
            profile.gaps.append("Experience gap")
            risk_flags += 1
            
        if profile.education_score < 50:
            profile.gaps.append("Education mismatch")
            risk_flags += 1
            
        if profile.behavior_score < 50:
            profile.gaps.append("Potential career instability")
            risk_flags += 1
            
        if profile.behavior_score == 0:
            profile.gaps.append("High likelihood honeypot candidate")
            risk_flags += 3
            
        if risk_flags >= 4:
            profile.risk_level = "High"
        elif risk_flags >= 2:
            profile.risk_level = "Medium"
        else:
            profile.risk_level = "Low"
