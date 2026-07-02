# AI Pipeline Document — AURA AI

## 1. Candidate Processing Pipeline
```
[Raw Candidate JSONL]
       ↓
[Pydantic Validation (schema.py)]
       ↓
[Extract demographic and career histories]
       ↓
[Calculate tenure, company profiles, and education tier attributes]
       ↓
[Persist Candidate DB Table (aura.db)]
```

---

## 2. Recruiter Job Intelligence Pipeline
```
[Job Description .docx File]
       ↓
[Extract XML zip structure & convert to raw text string]
       ↓
[Heuristic Regex extraction: required vs preferred skills, seniority, min experience]
       ↓
[Save as active Job Profile in repository]
```

---

## 3. Semantic Similarity Pipeline
1.  **Text Formatting:** Convert Candidate profiles and Job Descriptions into normalized paragraphs describing current titles, tenure, education tiers, and parsed skills lists.
2.  **Embedding Generation:** Pass formatted texts to `SentenceTransformer("all-MiniLM-L6-v2")` to generate unit-normalized 384-dimensional vectors.
3.  **Similarity Matrix:** Calculate the dot-product similarity (which equals cosine similarity for normalized vectors) between all candidate vectors and the active job vector:
    $$\text{Cosine Score} = \max(0.0, \mathbf{v}_{\text{candidate}} \cdot \mathbf{v}_{\text{job}}) \times 100.0$$
4.  **Top-K Slicing:** Sort scores using NumPy partitioning for high-speed indexing.

---

## 4. Multi-Dimensional Feature Pipeline
Candidates are scored across 6 specialized engines producing scores between $[0, 100]$:
1.  **SkillEngine:** Compares skills against Job required (80%) and preferred (20%) skill lists.
2.  **ExperienceEngine:** Evaluates total tenure, role title overlap, leadership keywords, stability, and career progress.
3.  **EducationEngine:** Rates school tiers, degree level (Masters/PhD), and STEM alignments.
4.  **CertificationEngine:** Verifies Cloud, AI/ML, Data, Devops, and Security credentials.
5.  **LanguageEngine:** Maps programming languages and fluent English levels.
6.  **BehaviorEngine:** Evaluates availability, recruiter response rate, and notice metrics.

---

## 5. Hybrid Ranking & Decision Pipeline
1.  **Aggregated Scoring:** Load weight profile from `profiles.yaml` and calculate the weighted overall score:
    $$\text{Overall Score} = \sum (\text{Dimension Score}_i \times \text{Weight}_i) / 100.0$$
2.  **Tie-Breaking:** Apply deterministic sorting priority: `(-overall_score, -semantic_score, -skill_score, -experience_score, candidate_id)`.
3.  **Decision Mapping:** Generate plain-text recommendation and confidence percentage from overall scores:
    *   $\text{Score} \ge 85 \implies \text{STRONG\_YES}$
    *   $70 \le \text{Score} < 85 \implies \text{YES}$
    *   $50 \le \text{Score} < 70 \implies \text{MAYBE}$
    *   $\text{Score} < 50 \implies \text{NO}$
