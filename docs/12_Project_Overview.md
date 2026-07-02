# Project Overview Document — AURA AI

## 1. Executive Summary
AURA AI represents the next generation of talent acquisition, moving industry standards from basic keyword filtration to a holistic, objective model combining **Semantic AI**, **Feature Intelligence**, **Hybrid Sorting**, and **Explainable AI**. 

By evaluating candidates across multiple independent dimensions and presenting plain-text explanations, the platform reduces time-to-hire, lowers false-negative screening errors, and maintains high trust with recruiters.

---

## 2. Platform Core Architecture Layout
```
[Candidate Profiles JSONL] ──────┐
                                 │
[Active Job Description DOCX] ───┼──→ [Semantic Embeddings & Feature Scores]
                                 │                      ↓
[Scoring Weight Config YAML] ────┘          [Aggregated Hybrid Rankings]
                                                        ↓
                                            [Submission Export Files]
```

---

## 3. Local Developer Setup Blueprint

### 3.1 Prerequisite Requirements
*   Python 3.12+ installed.
*   Node.js 18+ installed.

### 3.2 Backend Initialization
1.  Navigate to the backend folder:
    `cd backend`
2.  Set up the virtual environment:
    `python -m venv venv`
    `.\venv\Scripts\activate`
3.  Install requirements:
    `pip install -r requirements.txt`
4.  Run development server:
    `uvicorn app.core.main:app --reload --port 8000`

### 3.3 Frontend Initialization
1.  Navigate to the frontend folder:
    `cd ../frontend`
2.  Install packages:
    `npm install`
3.  Run client:
    `npm run dev`
