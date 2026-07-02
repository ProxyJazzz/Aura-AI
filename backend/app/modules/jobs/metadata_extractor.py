import re
from typing import Dict, Any
from app.modules.jobs.schema import Seniority, EmploymentType

COMMON_TITLES = [
    "ai engineer", "machine learning engineer", "ml engineer", "data scientist",
    "software engineer", "frontend engineer", "backend engineer", "fullstack engineer",
    "devops engineer", "data engineer", "analytics engineer", "cloud architect",
    "product manager", "solutions architect", "security engineer", "qa engineer",
    "ui/ux designer", "graphic designer", "project manager"
]

class JobMetadataExtractor:
    """Extracts job metadata from raw description text using rule heuristics."""

    @classmethod
    def extract_metadata(cls, text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return {
                "title": "Unknown Role",
                "min_experience": 0.0,
                "preferred_experience": 0.0,
                "seniority": Seniority.SENIOR,
                "employment_type": EmploymentType.FULL_TIME,
                "industry": "Technology",
                "location": "Remote",
                "remote_status": "remote"
            }

        # ── 1. Job Title ─────────────────────────────────────────────
        title = ""
        title_patterns = [
            r"^(?:job\s+)?title\s*:\s*(.*)$",
            r"^(?:role|position)\s*:\s*(.*)$",
            r"^opportunity\s*:\s*(.*)$"
        ]
        
        for line in lines[:5]:
            for pat in title_patterns:
                match = re.match(pat, line, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    break
            if title:
                break
                
        if not title:
            for line in lines[:3]:
                line_lower = line.lower()
                for c_title in COMMON_TITLES:
                    if c_title in line_lower:
                        title = line
                        break
                if title:
                    break
                    
        if not title:
            title = lines[0]
            
        title = re.sub(r"^[*\s#]+|[*\s#:]+$", "", title).strip()

        # ── 2. Experience ────────────────────────────────────────────
        min_exp = 0.0
        exp_patterns = [
            r"(?:minimum|min|at least|required|needs?)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?)",
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s*(?:of\s*)?experience",
            r"(\d+(?:\.\d+)?)\s*-\s*(\d+)\s*years?",
            r"(\d+(?:\.\d+)?)\s*to\s*(\d+)\s*years?"
        ]
        
        found_exp_vals = []
        for pat in exp_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    found_exp_vals.append(float(m[0]))
                else:
                    found_exp_vals.append(float(m))
                    
        if found_exp_vals:
            min_exp = min(found_exp_vals)

        # Preferred Experience
        pref_exp = min_exp + 2.0
        pref_exp_match = re.search(r"(?:preferred|desired)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?)", text, re.IGNORECASE)
        if pref_exp_match:
            pref_exp = float(pref_exp_match.group(1))

        # ── 3. Seniority ─────────────────────────────────────────────
        title_lower = title.lower()
        text_lower = text.lower()
        
        if any(w in title_lower for w in ["principal", "staff", "architect"]):
            seniority = Seniority.PRINCIPAL
        elif any(w in title_lower for w in ["lead", "manager", "head"]):
            seniority = Seniority.LEAD
        elif any(w in title_lower for w in ["senior", "sr", "experienced"]):
            seniority = Seniority.SENIOR
        elif any(w in title_lower for w in ["junior", "jr", "entry", "intern", "associate"]):
            seniority = Seniority.ENTRY
        elif "mid" in title_lower or "intermediate" in title_lower:
            seniority = Seniority.MID
        else:
            if "principal" in text_lower:
                seniority = Seniority.PRINCIPAL
            elif "lead engineer" in text_lower or "lead developer" in text_lower:
                seniority = Seniority.LEAD
            elif "senior" in text_lower or "sr." in text_lower:
                seniority = Seniority.SENIOR
            elif "junior" in text_lower or "intern" in text_lower or "entry level" in text_lower:
                seniority = Seniority.ENTRY
            else:
                seniority = Seniority.SENIOR

        # ── 4. Employment Type ───────────────────────────────────────
        employment_type = EmploymentType.FULL_TIME
        if "part-time" in text_lower or "part time" in text_lower:
            employment_type = EmploymentType.PART_TIME
        elif "contract" in text_lower:
            employment_type = EmploymentType.CONTRACT
        elif "freelance" in text_lower:
            employment_type = EmploymentType.FREELANCE
        elif "internship" in text_lower or "intern role" in text_lower:
            employment_type = EmploymentType.INTERNSHIP

        # ── 5. Industry ──────────────────────────────────────────────
        industry = "Technology"
        industries = {
            "fintech": "Fintech",
            "e-commerce": "E-commerce",
            "retail": "Retail / E-commerce",
            "healthcare": "Healthcare",
            "medical": "Healthcare",
            "automotive": "Automotive",
            "telecom": "Telecommunications",
            "gaming": "Gaming / Entertainment",
            "saas": "SaaS / Technology",
            "proptech": "Real Estate / Proptech",
            "paper": "Manufacturing / Supply Chain"
        }
        for ind_key, ind_val in industries.items():
            if ind_key in text_lower:
                industry = ind_val
                break

        # ── 6. Location & Remote Status ─────────────────────────────
        remote_status = "onsite"
        if "remote" in text_lower or "work from home" in text_lower or "wfh" in text_lower:
            remote_status = "remote"
        elif "hybrid" in text_lower:
            remote_status = "hybrid"

        location = "Remote" if remote_status == "remote" else "Unknown"
        location_match = re.search(r"\blocation\s*:\s*(.*)", text, re.IGNORECASE)
        if location_match:
            location = location_match.group(1).split("\n")[0].strip()
        else:
            for city in ["toronto", "san francisco", "bengaluru", "bangalore", "new york", "london", "berlin", "mumbai"]:
                if city in text_lower:
                    location = city.title()
                    break

        return {
            "title": title,
            "min_experience": min_exp,
            "preferred_experience": pref_exp,
            "seniority": seniority,
            "employment_type": employment_type,
            "industry": industry,
            "location": location,
            "remote_status": remote_status
        }
ClassName = JobMetadataExtractor
