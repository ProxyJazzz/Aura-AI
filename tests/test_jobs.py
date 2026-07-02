import io
import zipfile
import pytest
from fastapi.testclient import TestClient

from app.core.main import app
from app.modules.jobs.schema import Seniority, EmploymentType
from app.modules.jobs.service import JobService
from app.modules.jobs.repository import JobRepository

client = TestClient(app)

# ── Helper to create mock docx files in-memory ──────────────────────

def create_mock_docx(paragraphs: list) -> bytes:
    """Helper that builds a valid zip/docx package structure in-memory."""
    namespaces = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    
    # Construct word/document.xml content
    xml_str = f'<w:document {namespaces}><w:body>'
    for p in paragraphs:
        xml_str += f'<w:p><w:r><w:t>{p}</w:t></w:r></w:p>'
    xml_str += '</w:body></w:document>'
    
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w') as z:
        z.writestr('word/document.xml', xml_str)
    return bio.getvalue()

# ── Service Tests ────────────────────────────────────────────────

def test_docx_to_text_extraction():
    paragraphs = [
        "AURA AI Job Description",
        "We are looking for a Senior AI Engineer.",
        "Requirements:"
    ]
    docx_bytes = create_mock_docx(paragraphs)
    text = JobService.docx_to_text(docx_bytes)
    assert "AURA AI" in text
    assert "Senior AI Engineer" in text
    assert "\n" in text

def test_job_details_extraction_heuristics():
    doc_lines = [
        "Role: Machine Learning Engineer",
        "Domain: Fintech",
        "Requirements: Must have at least 4.5 years of experience in ML.",
        "Skills: Python, PyTorch, SQL, Docker",
        "Preferred qualifications:",
        "Kubernetes, FastAPI, RAG",
        "Soft Skills: Need good communication, teamwork, and mentorship."
    ]
    raw_text = "\n".join(doc_lines)
    job = JobService.extract_job_details(raw_text)
    
    assert job.title == "Machine Learning Engineer"
    assert job.min_experience == 4.5
    assert job.seniority == Seniority.SENIOR
    assert job.industry == "Fintech"
    assert job.employment_type == EmploymentType.FULL_TIME
    
    # Required skills
    assert "Python" in job.required_skills
    assert "PyTorch" in job.required_skills
    assert "SQL" in job.required_skills
    assert "Docker" in job.required_skills
    
    # Preferred skills (due to Preferred Qualifications heading)
    assert "FastAPI" in job.preferred_skills
    assert "Kubernetes" in job.preferred_skills
    assert "RAG" in job.preferred_skills
    
    # Soft skills
    assert "Communication" in job.soft_skills
    assert "Teamwork" in job.soft_skills
    assert "Mentorship" in job.soft_skills

# ── Endpoint Tests ───────────────────────────────────────────────

def test_job_flow_endpoints():
    # 1. Access current job when database is empty
    # Ensure tables are initialized first so the DELETE query doesn't fail
    JobRepository.create_tables()
    with get_db_connection() as conn:
        conn.execute("DELETE FROM jobs;")
        
    response = client.get("/api/v1/jobs/current")
    assert response.status_code == 404
    
    response = client.get("/api/v1/jobs/summary")
    assert response.status_code == 404
    
    # 2. Upload a mock docx job description
    paragraphs = [
        "Title: Senior AI Engineer",
        "Domain: Healthcare",
        "Employment Type: Full-time",
        "Experience: 6+ years of experience required.",
        "Key requirements:",
        "Python, PyTorch, Git",
        "Preferred qualifications (Nice to have):",
        "Docker, FastAPI, Kubernetes",
        "About the role: Require strong problem-solving and collaboration skills."
    ]
    docx_bytes = create_mock_docx(paragraphs)
    
    response = client.post(
        "/api/v1/jobs/upload",
        files={"file": ("job_description.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 201
    job_data = response.json()
    assert job_data["title"] == "Senior AI Engineer"
    assert job_data["min_experience"] == 6.0
    assert "Python" in job_data["required_skills"]
    assert "FastAPI" in job_data["preferred_skills"]
    
    # 3. Retrieve current job
    response = client.get("/api/v1/jobs/current")
    assert response.status_code == 200
    current_job = response.json()
    assert current_job["id"] == job_data["id"]
    assert current_job["title"] == "Senior AI Engineer"
    
    # 4. Retrieve job summary
    response = client.get("/api/v1/jobs/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["title"] == "Senior AI Engineer"
    assert summary["required_skills_count"] == 3
    assert summary["preferred_skills_count"] == 3
    assert summary["min_experience_years"] == 6.0
    assert summary["soft_skills_count"] == 2  # Problem-solving, Collaboration

def test_txt_file_upload():
    # TXT is now supported in Phase 3
    txt_content = """
    Role: Backend Developer
    Experience: 3 years of experience.
    Requirements:
    Python, SQL
    """
    response = client.post(
        "/api/v1/jobs/upload",
        files={"file": ("job.txt", txt_content.encode("utf-8"), "text/plain")}
    )
    assert response.status_code == 201
    job_data = response.json()
    assert job_data["title"] == "Backend Developer"
    assert job_data["min_experience"] == 3.0
    assert "Python" in job_data["required_skills"]


def test_invalid_file_upload():
    # Unsupported formats should still fail
    response = client.post(
        "/api/v1/jobs/upload",
        files={"file": ("test.pdf", b"pdf content", "application/pdf")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_job_phase3_new_endpoints():
    JobRepository.create_tables()
    with get_db_connection() as conn:
        conn.execute("DELETE FROM jobs;")

    # Upload a job description to populate database
    paragraphs = [
        "Title: Lead Python Developer",
        "Domain: Fintech",
        "Experience: 8 years required.",
        "Key requirements:",
        "Python, SQL, AWS",
        "Preferred qualifications:",
        "FastAPI, Docker",
        "Soft skills: Leadership"
    ]
    docx_bytes = create_mock_docx(paragraphs)
    
    # 1. First upload
    response = client.post(
        "/api/v1/jobs/upload",
        files={"file": ("job_desc_p3.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 201
    
    # 2. Get active hiring profile
    response = client.get("/api/v1/jobs/profile")
    assert response.status_code == 200
    profile = response.json()
    assert profile["metadata"]["title"] == "Lead Python Developer"
    assert "Python" in profile["requirements"]["required_skills"]
    assert "Summary" in profile["sections"]

    # 3. Get history
    response = client.get("/api/v1/jobs/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 1
    assert history[0]["filename"] == "job_desc_p3.docx"

    # 4. Get status
    response = client.get("/api/v1/jobs/status")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["has_active_job"] is True
    assert status_data["active_job_title"] == "Lead Python Developer"

    # 5. Duplicate upload check
    response = client.post(
        "/api/v1/jobs/upload",
        files={"file": ("job_desc_p3.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 400
    assert "already been uploaded" in response.json()["detail"]

    # 6. Delete/deactivate current active job
    response = client.delete("/api/v1/jobs/current")
    assert response.status_code == 200
    
    # Status should show no active job
    response = client.get("/api/v1/jobs/status")
    assert response.json()["has_active_job"] is False


# Import helper inside tests to avoid circular import issues
from app.shared.database import get_db_connection


