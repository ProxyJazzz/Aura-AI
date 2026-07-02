import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Tuple, Optional
from loguru import logger

from app.modules.jobs.schema import JobModel, Seniority, EmploymentType

# ── Tech Skills & Soft Skills Dictionaries ────────────────────────

ALL_TECH_SKILLS = [
    # AI/ML/Data Science
    "python", "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
    "machine learning", "ml", "deep learning", "nlp", "natural language processing", "computer vision",
    "cv", "reinforcement learning", "large language model", "llm", "transformers", "bert", "gpt",
    "rag", "embeddings", "vector database", "weaviate", "pinecone", "qdrant", "milvus", "faiss",
    "neural network", "fine-tuning", "lora", "qlora", "gan", "speech recognition", "tts",
    # Data Engineering & Databases
    "sql", "nosql", "spark", "pyspark", "airflow", "kafka", "dbt", "snowflake", "mongodb", "redis",
    "postgres", "postgresql", "mysql", "cassandra", "elastic", "elasticsearch",
    # Cloud & DevOps
    "docker", "kubernetes", "k8s", "aws", "gcp", "azure", "ci/cd", "jenkins", "git", "github",
    "terraform", "ansible", "linux", "unix",
    # Programming Languages
    "go", "golang", "java", "scala", "c++", "c#", "rust", "typescript", "javascript", "js", "ts",
    "ruby", "php", "swift", "kotlin",
    # Web Frameworks & UI
    "react", "angular", "vue", "next.js", "node.js", "flask", "fastapi", "django", "tailwind",
    "html", "css", "grpc", "graphql", "rest api"
]

ALL_SOFT_SKILLS = [
    "communication", "leadership", "collaboration", "mentorship", "problem-solving",
    "critical thinking", "agile", "adaptability", "creativity", "presentation",
    "teamwork", "analytical", "interpersonal", "project management", "time management",
    "decision-making", "negotiation", "work ethic"
]

COMMON_TITLES = [
    "ai engineer", "machine learning engineer", "ml engineer", "data scientist",
    "software engineer", "frontend engineer", "backend engineer", "fullstack engineer",
    "devops engineer", "data engineer", "analytics engineer", "cloud architect",
    "product manager", "solutions architect", "security engineer", "qa engineer",
    "ui/ux designer", "graphic designer", "project manager"
]

class JobService:
    """Service handling DOCX ingestion, text extraction, cleaning, and heuristic metadata parsing."""

    @staticmethod
    def docx_to_text(file_bytes: bytes) -> str:
        """Extract paragraphs and tables text from a DOCX file byte stream."""
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                xml_content = z.read('word/document.xml')
                root = ET.fromstring(xml_content)
                
                paragraphs = []
                # Walk through all XML elements to preserve document structure order
                for elem in root.iter():
                    if elem.tag.endswith('p'):
                        # Gather all text elements in the paragraph
                        texts = [t.text for t in elem.findall('.//w:t', namespaces) if t.text]
                        text_str = ''.join(texts).strip()
                        if text_str:
                            paragraphs.append(text_str)
                    elif elem.tag.endswith('tr'):
                        # Gather cell texts in a table row
                        cells = []
                        for tc in elem.findall('.//w:tc', namespaces):
                            cell_texts = [t.text for t in tc.findall('.//w:t', namespaces) if t.text]
                            cells.append(''.join(cell_texts).strip())
                        cells_str = ' | '.join(c for c in cells if c)
                        if cells_str:
                            paragraphs.append(cells_str)
                            
                return '\n'.join(paragraphs)
        except Exception as e:
            logger.error("Error unzipping/parsing DOCX payload: {err}", err=str(e))
            raise ValueError(f"Invalid DOCX file format: {str(e)}")

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean up spacing, remove redundant line endings, and normalize formatting characters."""
        # Replace multiple spaces with a single space
        text = re.sub(r"[ \t]+", " ", text)
        # Standardize carriage returns
        text = text.replace("\r", "")
        # Remove consecutive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def extract_job_details(cls, raw_text: str) -> JobModel:
        """
        Run regex & keyword-matching heuristics to parse raw job text into a structured JobModel.
        """
        cleaned = cls.clean_text(raw_text)
        lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
        
        if not lines:
            return JobModel(title="Unknown Role")
            
        # ── 1. Job Title Extraction ──────────────────────────────────
        title = ""
        # Search the first 5 lines for explicitly stated title patterns
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
                
        # If no explicit pattern match, look for common job title keywords in the first 3 lines
        if not title:
            for line in lines[:3]:
                line_lower = line.lower()
                for c_title in COMMON_TITLES:
                    if c_title in line_lower:
                        # Grab the line containing the title
                        title = line
                        break
                if title:
                    break
                    
        # Fallback: Use the very first line as title
        if not title:
            title = lines[0]
            
        # Clean title from trailing colons/formatting
        title = re.sub(r"^[*\s#]+|[*\s#:]+$", "", title).strip()

        # ── 2. Minimum Experience Extraction ─────────────────────────
        min_exp = 0.0
        exp_patterns = [
            r"(?:minimum|min|at least|required|needs?)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?)",
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s*(?:of\s*)?experience",
            r"(\d+(?:\.\d+)?)\s*-\s*(\d+)\s*years?",
            r"(\d+(?:\.\d+)?)\s*to\s*(\d+)\s*years?"
        ]
        
        found_exp_vals = []
        for pat in exp_patterns:
            matches = re.findall(pat, cleaned, re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    found_exp_vals.append(float(m[0]))
                else:
                    found_exp_vals.append(float(m))
                    
        if found_exp_vals:
            # Take the lowest experience requirement found
            min_exp = min(found_exp_vals)

        # ── 3. Seniority Extraction ──────────────────────────────────
        title_lower = title.lower()
        text_lower = cleaned.lower()
        
        # Check title first, then text content
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
            # Try matching text
            if "principal" in text_lower:
                seniority = Seniority.PRINCIPAL
            elif "lead engineer" in text_lower or "lead developer" in text_lower:
                seniority = Seniority.LEAD
            elif "senior" in text_lower or "sr." in text_lower:
                seniority = Seniority.SENIOR
            elif "junior" in text_lower or "intern" in text_lower or "entry level" in text_lower:
                seniority = Seniority.ENTRY
            else:
                seniority = Seniority.SENIOR  # default fallback

        # ── 4. Employment Type Extraction ────────────────────────────
        employment_type = EmploymentType.FULL_TIME
        if "part-time" in text_lower or "part time" in text_lower:
            employment_type = EmploymentType.PART_TIME
        elif "contract" in text_lower:
            employment_type = EmploymentType.CONTRACT
        elif "freelance" in text_lower:
            employment_type = EmploymentType.FREELANCE
        elif "internship" in text_lower or "intern role" in text_lower:
            employment_type = EmploymentType.INTERNSHIP

        # ── 5. Industry/Domain Extraction ────────────────────────────
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

        # ── 6. Skills Segmentation (Required vs Preferred) ────────────
        # To divide required vs preferred, we segment text into paragraphs/sections.
        # Find lines that look like headers containing "preferred", "pluses", "nice to", "bonus".
        pref_sections = []
        is_in_pref = False
        
        # Segment paragraphs based on headers
        pref_header_patterns = [
            r"preferred\s*(?:skills|qualifications|experience|requirements)",
            r"nice\s+to\s+have",
            r"pluses",
            r"bonus\s*points",
            r"desirable",
            r"like\s+you\s+to\s+have",
            r"would\s+like",
            r"won't\s+reject\s+you"
        ]
        
        exclude_header_patterns = [
            r"explicitly\s+do\s+not\s+want",
            r"do\s+not\s+want",
            r"disqualifiers"
        ]
        
        required_skills = set()
        preferred_skills = set()
        
        current_section_is_preferred = False
        current_section_is_excluded = False
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if this line is a section header (e.g. bold, bulletless, short, or starts a section)
            is_header = False
            
            # Simple header criteria: line ends with colon or is short and contains section words
            if len(line) < 60 and (line.endswith(":") or any(word in line_lower for word in ["requirements", "skills", "qualifications", "who you are", "about you", "what we look", "do not want", "disqualifiers"])):
                is_header = True
                
            if is_header:
                if any(re.search(pat, line_lower) for pat in pref_header_patterns):
                    current_section_is_preferred = True
                    current_section_is_excluded = False
                elif any(re.search(pat, line_lower) for pat in exclude_header_patterns):
                    current_section_is_preferred = False
                    current_section_is_excluded = True
                else:
                    # Some other header like "Requirements" or "What you do"
                    current_section_is_preferred = False
                    current_section_is_excluded = False
                    
            if current_section_is_excluded:
                continue
                
            # Extract skills in this line
            line_skills = []
            for skill in ALL_TECH_SKILLS:
                escaped_skill = re.escape(skill)
                # Handle special casing for common terms
                if skill in ["go", "cv", "ml", "ts", "js"]:
                    pattern = rf"\b{escaped_skill}\b"
                else:
                    pattern = rf"\b{escaped_skill}(?:s|\b)"
                    
                if re.search(pattern, line_lower):
                    line_skills.append(skill)
            
            for s in line_skills:
                # Format skill name nicely
                fmt_skill = s.title()
                # Special formats
                special_formats = {
                    "Sql": "SQL", "Nosql": "NoSQL", "Ml": "ML", "Nlp": "NLP", "Cv": "CV",
                    "Llm": "LLM", "Bert": "BERT", "Gpt": "GPT", "Rag": "RAG", "Tts": "TTS",
                    "Aws": "AWS", "Gcp": "GCP", "C++": "C++", "C#": "C#", "Next.Js": "Next.js",
                    "Node.Js": "Node.js", "Rest Api": "REST API", "Ui/Ux Designer": "UI/UX Designer",
                    "Gan": "GAN", "Ci/Cd": "CI/CD", "Js": "JavaScript", "Ts": "TypeScript",
                    "Pytorch": "PyTorch", "Tensorflow": "TensorFlow", "Scikit-Learn": "Scikit-Learn",
                    "Fastapi": "FastAPI"
                }
                final_skill = special_formats.get(fmt_skill, fmt_skill)
                
                if current_section_is_preferred:
                    preferred_skills.add(final_skill)
                else:
                    required_skills.add(final_skill)
                    
        # Clean up overlaps: if a skill is in required, it shouldn't be in preferred
        preferred_skills -= required_skills

        # ── 7. Soft Skills Extraction ────────────────────────────────
        soft_skills = set()
        soft_skills_map = {
            "Communication": [r"\bcommunication\b", r"\bwrit\w*\b", r"\bpresentation\b"],
            "Mentorship": [r"\bmentor\w*\b"],
            "Collaboration": [r"\bcollaborat\w*\b"],
            "Teamwork": [r"\bteam\w*\b"],
            "Leadership": [r"\blead\w*\b", r"\bmanag\w*\b"],
            "Problem-Solving": [r"\bproblem[- ]solving\b", r"\bsolv\w*\s+problem\w*\b"]
        }
        
        for skill_name, patterns in soft_skills_map.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    soft_skills.add(skill_name)
                    break

        return JobModel(
            title=title,
            required_skills=sorted(list(required_skills)),
            preferred_skills=sorted(list(preferred_skills)),
            min_experience=min_exp,
            seniority=seniority,
            industry=industry,
            employment_type=employment_type,
            soft_skills=sorted(list(soft_skills))
        )

    @classmethod
    def get_active_job(cls) -> Optional[Dict[str, Any]]:
        """Retrieve the currently active job description."""
        from app.modules.jobs.repository import JobRepository
        return JobRepository.get_active_job()
