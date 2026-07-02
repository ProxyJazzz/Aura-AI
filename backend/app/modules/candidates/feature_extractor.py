import json
from datetime import date
from typing import Dict, Any, Optional

from app.modules.candidates.schema import CandidateModel, SkillProficiency


class CandidateFeatureExtractor:
    """Generates derived features from raw candidate data models."""

    REFERENCE_DATE = date(2026, 7, 2)

    # Keywords to detect consulting/services companies
    CONSULTING_COMPANIES = {
        "tcs", "tata consultancy", "infosys", "wipro", "accenture", "cognizant", "cts",
        "capgemini", "mindtree", "tech mahindra", "l&t", "lnt", "hcl", "wipro technologies",
        "infosys limited", "accenture solutions", "cognizant technology solutions"
    }

    # Keywords to detect AI/ML skills
    AI_ML_KEYWORDS = {
        "machine learning", "ml", "artificial intelligence", "ai", "deep learning", "nlp",
        "natural language processing", "computer vision", "cv", "reinforcement learning",
        "large language model", "llm", "transformers", "pytorch", "tensorflow", "keras",
        "scikit-learn", "sklearn", "bert", "gpt", "rag", "embeddings", "vector database",
        "pinecone", "weaviate", "qdrant", "milvus", "faiss", "neural network", "fine-tuning",
        "lora", "qlora", "gan", "speech recognition", "text-to-speech", "tts"
    }

    @classmethod
    def is_consulting_company(cls, company_name: str) -> bool:
        """Check if a company is a services/consulting company."""
        name_lower = company_name.lower().strip()
        return any(keyword in name_lower for keyword in cls.CONSULTING_COMPANIES)

    @classmethod
    def detect_honeypot(cls, candidate: CandidateModel) -> bool:
        """Detect subtly impossible or inconsistent profiles (Honeypots)."""
        # 1. Expert zero duration skills check
        zero_duration_expert_skills = sum(
            1 for s in candidate.skills
            if s.proficiency == SkillProficiency.EXPERT and s.duration_months == 0
        )
        if zero_duration_expert_skills >= 1:
            return True

        # 2. Single job exceeds total experience check
        total_exp_months = candidate.profile.years_of_experience * 12
        for job in candidate.career_history:
            if job.duration_months > total_exp_months + 6:
                return True

        # 3. Sum of all jobs exceeds total experience check
        sum_durations = sum(job.duration_months for job in candidate.career_history)
        if sum_durations > total_exp_months + 24:
            return True

        # 4. Job date vs duration consistency check
        for job in candidate.career_history:
            try:
                start = date.fromisoformat(job.start_date)
                if job.is_current or not job.end_date:
                    end = cls.REFERENCE_DATE
                else:
                    end = date.fromisoformat(job.end_date)

                diff_days = (end - start).days
                expected_months = int(round(diff_days / 30.4375))

                if abs(expected_months - job.duration_months) > 3:
                    return True
            except Exception:
                pass

        return False

    @classmethod
    def extract_features(cls, candidate: CandidateModel) -> Dict[str, Any]:
        """Extract analytical and behavioral features from a validated candidate profile."""
        profile = candidate.profile
        signals = candidate.redrob_signals

        # ── Skills features ──────────────────────────────────────────
        skill_names = [s.name for s in candidate.skills]
        skills_list = ", ".join(skill_names)
        primary_skills_count = len(skill_names)

        # Check for AI/ML skills
        has_ai_ml_skills = 0
        for name in skill_names:
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in cls.AI_ML_KEYWORDS):
                has_ai_ml_skills = 1
                break

        # ── Experience features ──────────────────────────────────────
        years_of_experience = profile.years_of_experience

        # Consulting firm checks
        worked_companies = [job.company for job in candidate.career_history]
        consulting_flags = [cls.is_consulting_company(c) for c in worked_companies]

        has_worked_in_consulting = 1 if any(consulting_flags) else 0
        has_only_consulting_experience = 1 if (consulting_flags and all(consulting_flags)) else 0

        num_companies = len(set(worked_companies))

        # Calculate tenure stats
        durations = [job.duration_months for job in candidate.career_history]
        avg_tenure_months = sum(durations) / len(durations) if durations else 0.0

        # ── Education features ───────────────────────────────────────
        highest_tier = "unknown"
        tier_values = {"tier_1": 1, "tier_2": 2, "tier_3": 3, "tier_4": 4, "unknown": 5}

        has_masters_or_phd = 0

        for edu in candidate.education:
            # Find the best tier (lowest value represents highest prestige)
            current_tier = edu.tier.value if hasattr(edu.tier, 'value') else str(edu.tier)
            if tier_values.get(current_tier, 5) < tier_values.get(highest_tier, 5):
                highest_tier = current_tier

            deg_lower = edu.degree.lower()
            if any(term in deg_lower for term in ["m.s.", "ms", "m.sc", "msc", "m.e.", "me", "m.tech", "mtech", "ph.d", "phd", "mba"]):
                has_masters_or_phd = 1

        # ── Certifications & Languages ───────────────────────────────
        num_certifications = len(candidate.certifications)
        num_languages = len(candidate.languages)

        # ── Behavioral features ──────────────────────────────────────
        profile_completeness_score = signals.profile_completeness_score
        recruiter_response_rate = signals.recruiter_response_rate
        avg_response_time_hours = signals.avg_response_time_hours
        open_to_work_flag = 1 if signals.open_to_work_flag else 0

        # Calculate recency of last active date
        last_active_date_str = signals.last_active_date

        # Detect if candidate is a honeypot
        is_honeypot = 1 if cls.detect_honeypot(candidate) else 0

        return {
            "candidate_id": candidate.candidate_id,
            "is_valid": 1,
            "is_honeypot": is_honeypot,
            "validation_error": None,
            "raw_json": json.dumps(candidate.model_dump()),

            # Features
            "anonymized_name": profile.anonymized_name,
            "location": profile.location,
            "country": profile.country,
            "years_of_experience": years_of_experience,
            "current_title": profile.current_title,
            "current_company": profile.current_company,
            "profile_completeness_score": profile_completeness_score,
            "recruiter_response_rate": recruiter_response_rate,
            "avg_response_time_hours": avg_response_time_hours,
            "open_to_work_flag": open_to_work_flag,
            "skills_list": skills_list,
            "primary_skills_count": primary_skills_count,
            "has_ai_ml_skills": has_ai_ml_skills,
            "has_only_consulting_experience": has_only_consulting_experience,
            "has_worked_in_consulting": has_worked_in_consulting,
            "num_companies": num_companies,
            "avg_tenure_months": avg_tenure_months,
            "highest_education_tier": highest_tier,
            "has_masters_or_phd": has_masters_or_phd,
            "num_certifications": num_certifications,
            "num_languages": num_languages,
            "last_active_date": last_active_date_str
        }
