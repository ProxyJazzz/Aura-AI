# Deployment Architecture Document — AURA AI

## 1. Cloud Infrastructure Model
AURA AI is designed to deploy on **Render** (or Docker) as a Web Service. Relational data sits on a persistent disk mounted directly to the container to ensure SQLite `aura.db` writes are preserved.

---

## 2. Intended `render.yaml` Structure
```yaml
services:
  - type: web
    name: aura-ai-backend
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.core.main:app --host 0.0.0.0 --port 8000
    envVars:
      - key: APP_ENV
        value: production
      - key: DATABASE_URL
        value: sqlite:////var/data/aura.db
      - key: TRANSFORMERS_OFFLINE
        value: "1"
      - key: HF_HUB_OFFLINE
        value: "1"
    disk:
      name: aura-sqlite-storage
      mountPath: /var/data
      sizeGB: 10
```

---

## 3. Environment Variable Manifest
*   `APP_ENV`: Deployment state (`development` or `production`).
*   `DATABASE_URL`: Location URI for sqlite.
*   `CORS_ORIGINS`: Allowed request endpoints (JSON array format).
*   `TRANSFORMERS_OFFLINE`: Forces SentenceTransformers to bypass remote downloads and load the local cached `all-MiniLM-L6-v2` file.
