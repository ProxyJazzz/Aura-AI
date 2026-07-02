import re
from typing import List, Dict, Set

ALL_TECH_SKILLS = [
    "python", "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
    "machine learning", "ml", "deep learning", "nlp", "natural language processing", "computer vision",
    "cv", "reinforcement learning", "large language model", "llm", "transformers", "bert", "gpt",
    "rag", "embeddings", "vector database", "weaviate", "pinecone", "qdrant", "milvus", "faiss",
    "neural network", "fine-tuning", "lora", "qlora", "gan", "speech recognition", "tts",
    "sql", "nosql", "spark", "pyspark", "airflow", "kafka", "dbt", "snowflake", "mongodb", "redis",
    "postgres", "postgresql", "mysql", "cassandra", "elastic", "elasticsearch",
    "docker", "kubernetes", "k8s", "aws", "gcp", "azure", "ci/cd", "jenkins", "git", "github",
    "terraform", "ansible", "linux", "unix",
    "go", "golang", "java", "scala", "c++", "c#", "rust", "typescript", "javascript", "js", "ts",
    "ruby", "php", "swift", "kotlin",
    "react", "angular", "vue", "next.js", "node.js", "flask", "fastapi", "django", "tailwind",
    "html", "css", "grpc", "graphql", "rest api"
]

ALL_SOFT_SKILLS = {
    "Communication": [r"\bcommunication\b", r"\bwrit\w*\b", r"\bpresentation\b"],
    "Mentorship": [r"\bmentor\w*\b"],
    "Collaboration": [r"\bcollaborat\w*\b"],
    "Teamwork": [r"\bteam\w*\b"],
    "Leadership": [r"\blead\w*\b", r"\bmanag\w*\b"],
    "Problem-Solving": [r"\bproblem[- ]solving\b", r"\bsolv\w*\s+problem\w*\b"]
}

CERTIFICATION_PATTERNS = [
    r"\baws\s+certified\b", r"\bazure\s+certified\b", r"\bgcp\s+certified\b", r"\bcka\b", r"\bcomp-tia\b", r"\bpmp\b", r"\bscrum\s+master\b"
]

EDUCATION_PATTERNS = [
    r"\bbachelors?\b", r"\bmasters?\b", r"\bph\.?d\b", r"\bbs\b", r"\bms\b", r"\bcomputer\s+science\b"
]

LANGUAGE_PATTERNS = [
    r"\benglish\b", r"\bgerman\b", r"\bhindi\b", r"\bspanish\b", r"\bfrench\b", r"\bjapanese\b"
]

class JobRequirementClassifier:
    """Classifies tech skills, soft skills, certifications, education, languages, and exclusions."""

    @classmethod
    def classify_requirements(cls, sections: Dict[str, str]) -> Dict[str, List[str]]:
        req_text = (sections.get("Requirements", "") + "\n" + sections.get("Summary", "")).lower()
        pref_text = (sections.get("Preferred Qualifications", "") + "\n" + sections.get("Nice To Have", "")).lower()
        full_text = "\n".join(sections.values()).lower()

        required_tech = set()
        preferred_tech = set()
        soft_skills = set()
        certs = set()
        edu = set()
        langs = set()
        negative_reqs = set()

        # ── 1. Tech Skills ───────────────────────────────────────────
        for skill in ALL_TECH_SKILLS:
            escaped = re.escape(skill)
            if skill in ["go", "cv", "ml", "ts", "js"]:
                pattern = rf"\b{escaped}\b"
            else:
                pattern = rf"\b{escaped}(?:s|\b)"

            # Map skill formatting
            fmt_skill = skill.title()
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

            if re.search(pattern, pref_text):
                preferred_tech.add(final_skill)
            elif re.search(pattern, req_text):
                required_tech.add(final_skill)
            elif re.search(pattern, full_text):
                required_tech.add(final_skill)

        # Remove overlaps
        preferred_tech -= required_tech

        # ── 2. Soft Skills ───────────────────────────────────────────
        for sname, patterns in ALL_SOFT_SKILLS.items():
            for pat in patterns:
                if re.search(pat, full_text):
                    soft_skills.add(sname)
                    break

        # ── 3. Certifications ────────────────────────────────────────
        for pat in CERTIFICATION_PATTERNS:
            match = re.search(pat, full_text)
            if match:
                certs.add(match.group(0).upper())

        # ── 4. Education ─────────────────────────────────────────────
        for pat in EDUCATION_PATTERNS:
            match = re.search(pat, full_text)
            if match:
                edu.add(match.group(0).title())

        # ── 5. Languages ─────────────────────────────────────────────
        for pat in LANGUAGE_PATTERNS:
            match = re.search(pat, full_text)
            if match:
                langs.add(match.group(0).title())

        # ── 6. Negative Requirements ──────────────────────────────────
        # Check exclusion section or lines with negative indicators
        excl_text = sections.get("Exclusions", "")
        if excl_text:
            for line in excl_text.split("\n"):
                if line.strip():
                    negative_reqs.add(line.strip())
        
        # Scan general text for negatives like "no agency", "do not apply if"
        neg_patterns = [
            r"\b(?:no\s+agencies|no\s+visas?|do\s+not\s+apply\s+if)\b.*"
        ]
        for pat in neg_patterns:
            matches = re.findall(pat, full_text)
            for m in matches:
                negative_reqs.add(m.strip())

        return {
            "required_skills": sorted(list(required_tech)),
            "preferred_skills": sorted(list(preferred_tech)),
            "soft_skills": sorted(list(soft_skills)),
            "certifications": sorted(list(certs)),
            "education": sorted(list(edu)),
            "languages": sorted(list(langs)),
            "negative_requirements": sorted(list(negative_reqs))
        }
