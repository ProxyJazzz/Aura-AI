import json
from typing import Dict, Any

def format_candidate_text(candidate: Dict[str, Any]) -> str:
    """
    Format candidate database features and raw timeline descriptions into a rich text paragraph.
    This helps SentenceTransformers capture deep semantic experience beyond keyword matching.
    """
    parts = []
    
    # 1. Base Metadata
    parts.append(f"Candidate Title: {candidate.get('current_title', 'Software Engineer')}.")
    parts.append(f"Years of Experience: {candidate.get('years_of_experience', 0.0)} years.")
    parts.append(f"Skills: {candidate.get('skills_list', '')}.")
    
    # Format Education Tier nicely
    edu_tier = candidate.get('highest_education_tier', 'unknown').replace('_', ' ').title()
    parts.append(f"Education: {edu_tier}.")
    
    # 2. Extract rich text fields from raw JSON
    raw_json_str = candidate.get("raw_json")
    if raw_json_str:
        try:
            raw_data = json.loads(raw_json_str)
            profile = raw_data.get("profile", {})
            headline = profile.get("headline", "")
            summary = profile.get("summary", "")
            
            if headline:
                parts.append(f"Headline: {headline}")
            if summary:
                parts.append(f"Summary: {summary}")
                
            # Grab all career descriptions
            career_history = raw_data.get("career_history", [])
            for job in career_history:
                company = job.get("company", "")
                title = job.get("title", "")
                desc = job.get("description", "")
                if desc:
                    parts.append(f"Worked at {company} as {title}: {desc}")

            # Certifications
            certs = raw_data.get("certifications", [])
            certs_str_list = []
            for cert in certs:
                name = cert.get("name")
                issuer = cert.get("issuer")
                year = cert.get("year")
                if name:
                    part = f"{name}"
                    if issuer or year:
                        info = []
                        if issuer:
                            info.append(f"issued by {issuer}")
                        if year:
                            info.append(f"in {year}")
                        part += f" ({', '.join(info)})"
                    certs_str_list.append(part)
            if certs_str_list:
                parts.append(f"Certifications: {', '.join(certs_str_list)}.")

            # Languages
            langs = raw_data.get("languages", [])
            langs_str_list = []
            for lang in langs:
                language = lang.get("language")
                proficiency = lang.get("proficiency")
                if language:
                    part = f"{language}"
                    if proficiency:
                        part += f" ({proficiency})"
                    langs_str_list.append(part)
            if langs_str_list:
                parts.append(f"Languages: {', '.join(langs_str_list)}.")
        except Exception:
            pass
            
    return " ".join(parts)

def format_job_text(job: Dict[str, Any]) -> str:
    """
    Format job description features and clean text into a rich query paragraph.
    """
    parts = []
    parts.append(f"Job Title: {job['title']}.")
    
    # Map enum/string inputs safely
    seniority = job.get("seniority")
    seniority_val = seniority.value if hasattr(seniority, "value") else str(seniority)
    parts.append(f"Seniority Required: {seniority_val}.")
    
    parts.append(f"Industry Domain: {job.get('industry', 'Technology')}.")
    
    req_skills = job.get("required_skills", [])
    if req_skills:
        parts.append(f"Required Technical Skills: {', '.join(req_skills)}.")
        
    pref_skills = job.get("preferred_skills", [])
    if pref_skills:
        parts.append(f"Preferred Nice-to-Have Skills: {', '.join(pref_skills)}.")
        
    soft_skills = job.get("soft_skills", [])
    if soft_skills:
        parts.append(f"Required Soft Skills: {', '.join(soft_skills)}.")
        
    # Append the raw text of the job description (limit to first 3000 chars to save embedding width)
    raw_text = job.get("raw_text", "")
    if raw_text:
        parts.append(f"Detailed Job Description: {raw_text[:3000]}")
        
    return " ".join(parts)
