from app.modules.decision.decision_profile import DecisionProfile

class ReasonEngine:
    """Generates deterministic explanations from existing scores without LLM."""

    @classmethod
    def evaluate(cls, profile: DecisionProfile):
        """Map dimension scores into structured deterministic explanation strings (Strengths/Reason Codes)."""
        
        if profile.semantic_score >= 80:
            profile.strengths.append("High semantic context match")
            profile.reason_codes.append("SEMANTIC_FIT_HIGH")
        
        if profile.skill_score >= 80:
            profile.strengths.append("Exceptional skill alignment")
            profile.reason_codes.append("SKILL_MATCH")
            
        if profile.experience_score >= 80:
            profile.strengths.append("Strong relevant experience")
            profile.reason_codes.append("EXPERIENCE_MATCH")
            
        if profile.education_score >= 80:
            profile.strengths.append("Exceeds education requirements")
            profile.reason_codes.append("EDUCATION_MATCH")
            
        if profile.certification_score >= 80:
            profile.strengths.append("Relevant certifications present")
            profile.reason_codes.append("CERT_MATCH")
            
        if profile.language_score >= 80:
            profile.strengths.append("Strong language proficiency")
            profile.reason_codes.append("LANGUAGE_MATCH")
            
        if profile.behavior_score >= 80:
            profile.strengths.append("Stable career history")
            profile.reason_codes.append("BEHAVIOR_MATCH")
