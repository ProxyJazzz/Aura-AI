<div align="center">

# ✨ AURA AI

### Hiring Beyond Keywords.

**AI Recruitment Intelligence Platform**

Semantically understand job descriptions and candidate profiles. Rank candidates using hybrid AI scoring. Produce explainable recommendations.

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-Strict-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## 🎯 What is AURA AI?

Traditional ATS systems rely on keyword matching and frequently miss highly qualified candidates. AURA AI solves this by:

- **Semantic Understanding** — Uses Sentence Transformers to deeply understand job descriptions and candidate profiles beyond keywords
- **Hybrid Scoring** — Combines semantic similarity, skills analysis, experience matching, and behavioral signals
- **Explainable AI** — Every ranking includes a transparent score breakdown with confidence levels
- **Enterprise UX** — Premium dark-themed interface inspired by Linear, Vercel, and OpenAI

## 🏗️ Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Framer Motion, Lucide, Recharts |
| **Backend** | Python 3.12, FastAPI, Pydantic v2, Uvicorn, Loguru |
| **AI/ML** | Sentence Transformers, NumPy, Pandas, Scikit-learn |
| **Deployment** | Vercel (frontend), Render (backend) |

## 📁 Project Structure

```
AURA-AI/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── core/           # Application factory, startup
│   │   ├── modules/        # Feature modules (health, jobs, candidates, ranking, analytics)
│   │   └── shared/         # Config, logging, exceptions, middleware, utils
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # React TypeScript frontend
│   ├── src/
│   │   ├── app/            # Providers, routes, layouts
│   │   ├── components/     # UI components (common, dashboard, etc.)
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   ├── hooks/          # Custom hooks
│   │   ├── store/          # State management
│   │   ├── types/          # TypeScript types
│   │   └── lib/            # Utilities, constants
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # Project documentation
├── datasets/                # Recruitment datasets
├── outputs/                 # AI-generated outputs
├── scripts/                 # Utility scripts
└── tests/                   # Test suites
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm 9+

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
uvicorn app.core.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at `http://localhost:5173`.

### Verify

```bash
# Health check
curl http://localhost:8000/api/v1/health
```

## 📋 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Application health check |

*Additional endpoints will be added in Sprint 1+.*

## 🎨 Design System

| Token | Value | Usage |
|---|---|---|
| Background | `#050816` | Page background |
| Surface | `#0F172A` | Cards, panels |
| Primary | `#7C5CFF` | Buttons, active states |
| Accent | `#00D4FF` | Highlights, badges |
| Success | `#22C55E` | Positive indicators |
| Warning | `#F59E0B` | Caution indicators |
| Danger | `#EF4444` | Error states |
| Text | `#F8FAFC` | Primary text |
| Muted | `#94A3B8` | Secondary text |

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built for the Hack2Skill INDIA.RUNS Data & AI Challenge**

Made with ❤️ by the AURA AI Team

</div>
