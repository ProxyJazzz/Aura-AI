import json
import os
import tempfile
from pathlib import Path
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.core.main import app
from app.modules.jobs.schema import Seniority
from app.modules.semantic.utils import format_candidate_text, format_job_text
from app.modules.semantic.embedding_service import EmbeddingService
from app.modules.semantic.cache_service import CacheService
from app.modules.semantic.similarity_service import SimilarityService
from app.modules.semantic.service import SemanticService

client = TestClient(app)

# ── 1. Text Formatting & Normalization Tests ──────────────────────

def test_text_formatting():
    candidate_dict = {
        "current_title": "AI Engineer",
        "years_of_experience": 6.5,
        "skills_list": "Python, PyTorch, LLM",
        "highest_education_tier": "tier_1",
        "raw_json": json.dumps({
            "profile": {
                "headline": "Lead AI Engineer",
                "summary": "Building modern LLM search engines."
            },
            "career_history": [
                {
                    "company": "Redrob",
                    "title": "Senior Engineer",
                    "description": "Shipped a semantic matching engine."
                }
            ]
        })
    }
    cand_text = format_candidate_text(candidate_dict)
    assert "Candidate Title: AI Engineer" in cand_text
    assert "Years of Experience: 6.5" in cand_text
    assert "Skills: Python, PyTorch, LLM" in cand_text
    assert "Education: Tier 1" in cand_text
    assert "Headline: Lead AI Engineer" in cand_text
    assert "Shipped a semantic matching engine" in cand_text

    job_dict = {
        "title": "Lead AI Architect",
        "seniority": Seniority.LEAD,
        "industry": "Fintech",
        "required_skills": ["Python", "Transformers", "SQL"],
        "preferred_skills": ["RAG", "Faiss"],
        "soft_skills": ["Mentorship", "Communication"],
        "raw_text": "We are seeking a Lead AI Architect to scale our search systems."
    }
    job_text = format_job_text(job_dict)
    assert "Job Title: Lead AI Architect" in job_text
    assert "Seniority Required: Lead" in job_text
    assert "Industry Domain: Fintech" in job_text
    assert "Required Technical Skills: Python, Transformers, SQL" in job_text
    assert "Preferred Nice-to-Have Skills: RAG, Faiss" in job_text
    assert "seeking a Lead AI Architect" in job_text

# ── 2. Embedding Model Singleton Loader Tests ────────────────────

def test_embedding_model_singleton():
    # Verify that get_model returns the same singleton model instance
    model1 = EmbeddingService.get_model()
    model2 = EmbeddingService.get_model()
    assert model1 is model2

def test_embedding_generation_correctness():
    # Encode a test text
    test_text = ["Lead Machine Learning Engineer specializing in NLP and search systems."]
    emb = EmbeddingService.generate_embeddings(test_text)
    
    assert isinstance(emb, np.ndarray)
    # Model returns shape (1, 384) for all-MiniLM-L6-v2
    assert emb.shape == (1, 384)
    assert emb.dtype == np.float32
    
    # Confirm unit-normalization: norm of vector should be approximately 1.0
    vector_norm = np.linalg.norm(emb[0])
    assert vector_norm == pytest.approx(1.0, rel=1e-4)

# ── 3. Cosine Similarity & Sorting Math Tests ───────────────────

def test_cosine_similarity_calculation():
    # Setup test vectors (already unit-normalized)
    # candidate 1 is identical to query (should get 100.0 score)
    # candidate 2 is orthogonal to query (should get 50.0 score with our map)
    query_emb = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    matrix = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ], dtype=np.float32)
    
    scores = SimilarityService.compute_scores(matrix, query_emb)
    # identical: dot product = 1.0 -> score = 1.0 * 100 = 100.0
    # orthogonal: dot product = 0.0 -> score = 0.0 * 100 = 0.0
    assert scores[0] == pytest.approx(100.0)
    assert scores[1] == pytest.approx(0.0)

def test_argpartition_ranking_correctness():
    candidate_ids = ["CAND_1", "CAND_2", "CAND_3", "CAND_4"]
    scores = np.array([45.0, 89.5, 92.1, 12.0], dtype=np.float32)
    
    # Get top 2
    ranked = SimilarityService.rank_candidates(scores, candidate_ids, top_k=2)
    
    assert len(ranked) == 2
    # CAND_3 should be first (92.1)
    assert ranked[0][0] == "CAND_3"
    assert ranked[0][1] == pytest.approx(92.1)
    # CAND_2 should be second (89.5)
    assert ranked[1][0] == "CAND_2"
    assert ranked[1][1] == pytest.approx(89.5)

# ── 4. Cache Persistence Layer Tests ─────────────────────────────

def test_disk_cache_persistence():
    candidate_ids = ["C_001", "C_002"]
    vectors = np.random.randn(2, 384).astype(np.float32)
    # Normalize
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    
    # Use temporary file paths for cache test
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)
    
    with patch.object(CacheService, 'get_backend_root', return_value=temp_path):
        # 1. Check status empty
        status = CacheService.get_cache_status()
        assert status["is_built"] is False
        
        # 2. Save cache
        CacheService.save_cache(vectors, candidate_ids)
        
        # 3. Check status built
        status = CacheService.get_cache_status()
        assert status["is_built"] is True
        assert status["total_embeddings"] == 2
        assert status["cache_file_size_mb"] >= 0.0
        
        # 4. Load cache
        loaded_matrix, loaded_ids = CacheService.load_cache()
        assert loaded_ids == candidate_ids
        assert np.allclose(loaded_matrix, vectors)
        
        # 5. Clear cache
        CacheService.clear_cache()
        status = CacheService.get_cache_status()
        assert status["is_built"] is False
        
    temp_dir.cleanup()

# ── 5. Endpoints & REST Layer Tests ──────────────────────────────

@patch.object(EmbeddingService, 'generate_embeddings')
def test_semantic_matching_endpoints(mock_embed):
    # Setup mock vector embeddings dynamically matching input text size
    mock_embed.side_effect = lambda texts, *args, **kwargs: np.random.randn(len(texts), 384).astype(np.float32)
    
    # 1. Clear database cache files first
    response = client.delete("/api/v1/semantic/cache")
    assert response.status_code == 200
    
    response = client.get("/api/v1/semantic/status")
    assert response.status_code == 200
    assert response.json()["is_built"] is False
    
    # 2. Match Top Candidates should fail with 400 when cache is empty
    response = client.get("/api/v1/semantic/top?limit=10")
    assert response.status_code == 400
    
    # 3. Simulate cache builder.
    mock_candidates = [
        {
            "candidate_id": f"CAND_{i:07d}",
            "current_title": "AI Engineer",
            "skills_list": "Python, PyTorch",
            "years_of_experience": 5.0,
            "highest_education_tier": "tier_1",
            "raw_json": "{}"
        }
        for i in range(1, 6) # 5 mock candidates
    ]
    
    # Mock CandidateService inside build_candidate_embeddings_cache
    with patch('app.modules.candidates.service.CandidateService.get_valid_candidates', return_value=mock_candidates):
        # Build candidate embeddings cache directly (synchronous)
        SemanticService.build_candidate_embeddings_cache()
        
    # Check status is built
    response = client.get("/api/v1/semantic/status")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["is_built"] is True
    assert status_data["total_embeddings"] == 5

    # 4. Generate active job embedding. 
    # Setup a mock active job
    mock_job = {
        "id": "JOB_TEST001",
        "title": "Senior AI Architect",
        "raw_text": "We need PyTorch experience.",
        "required_skills": ["Python", "PyTorch"],
        "preferred_skills": [],
        "min_experience": 5.0,
        "seniority": "Senior",
        "industry": "Technology",
        "employment_type": "Full-time",
        "soft_skills": ["Leadership"],
        "created_at": "2026-07-02T09:00:00Z",
        "is_active": True
    }
    
    with patch('app.modules.jobs.service.JobService.get_active_job', return_value=mock_job):
        response = client.post("/api/v1/semantic/job")
        assert response.status_code == 200
        assert "Successfully generated and cached" in response.json()["message"]
        
        # 5. Query ranked top matching candidates
        mock_db_candidates = [
            {
                "candidate_id": f"CAND_{i:07d}",
                "anonymized_name": f"Candidate {i}",
                "current_title": "AI Engineer",
                "years_of_experience": 5.0,
                "location": "Noida",
                "skills_list": "Python, PyTorch"
            }
            for i in range(1, 6)
        ]
        
        with patch('app.modules.candidates.service.CandidateService.get_candidates_by_ids', return_value=mock_db_candidates):
            # Test valid limit choice
            response = client.get("/api/v1/semantic/top?limit=10")
            assert response.status_code == 200
            top_data = response.json()
            assert top_data["job_id"] == "JOB_TEST001"
            assert len(top_data["matches"]) == 5
            assert "score" in top_data["matches"][0]
            assert top_data["matches"][0]["experience"] == 5.0
            
            # Telemetry checks
            assert "model_load_time_ms" in top_data
            assert "similarity_time_ms" in top_data
            assert "memory_usage_mb" in top_data
            
            # Test invalid limit choice (returns 400)
            invalid_response = client.get("/api/v1/semantic/top?limit=3")
            assert invalid_response.status_code == 400
            
    # Clean up test cache files
    client.delete("/api/v1/semantic/cache")


@patch.object(EmbeddingService, 'generate_embeddings')
def test_semantic_debug_endpoint(mock_embed):
    # Setup mock vector embeddings dynamically matching input text size
    mock_embed.side_effect = lambda texts, *args, **kwargs: np.random.randn(len(texts), 384).astype(np.float32)
    
    # 1. Clear database cache files first
    client.delete("/api/v1/semantic/cache")
    
    # 2. Query debug endpoint when cache empty
    with patch('app.modules.jobs.service.JobService.get_active_job', return_value=None):
        response = client.get("/api/v1/semantic/debug")
        assert response.status_code == 200
        data = response.json()
        assert data["current_job"] is None
        assert len(data["top_5_candidates"]) == 0
        assert data["embedding_dimensions"] == 384
        assert data["cache_status"]["is_built"] is False
    
    # 3. Simulate cache build and active job
    mock_candidates = [
        {
            "candidate_id": f"CAND_{i:07d}",
            "current_title": "AI Engineer",
            "skills_list": "Python, PyTorch",
            "years_of_experience": 5.0,
            "highest_education_tier": "tier_1",
            "raw_json": "{}"
        }
        for i in range(1, 6)
    ]
    mock_job = {
        "id": "JOB_TEST001",
        "title": "Senior AI Architect",
        "raw_text": "We need PyTorch experience.",
        "required_skills": ["Python", "PyTorch"],
        "preferred_skills": [],
        "min_experience": 5.0,
        "seniority": "Senior",
        "industry": "Technology",
        "employment_type": "Full-time",
        "soft_skills": ["Leadership"],
        "created_at": "2026-07-02T09:00:00Z",
        "is_active": True
    }
    
    mock_db_candidates = [
        {
            "candidate_id": f"CAND_{i:07d}",
            "anonymized_name": f"Candidate {i}",
            "current_title": "AI Engineer",
            "years_of_experience": 5.0,
            "location": "Noida",
            "skills_list": "Python, PyTorch"
        }
        for i in range(1, 6)
    ]
    
    with patch('app.modules.candidates.service.CandidateService.get_valid_candidates', return_value=mock_candidates):
        SemanticService.build_candidate_embeddings_cache()
        
    with patch('app.modules.jobs.service.JobService.get_active_job', return_value=mock_job):
        client.post("/api/v1/semantic/job")
        
        with patch('app.modules.candidates.service.CandidateService.get_candidates_by_ids', return_value=mock_db_candidates):
            response = client.get("/api/v1/semantic/debug")
            assert response.status_code == 200
            data = response.json()
            assert data["current_job"]["id"] == "JOB_TEST001"
            assert len(data["top_5_candidates"]) == 5
            assert len(data["similarity_scores"]) == 5
            assert "peak_memory_usage_mb" in data["performance_metrics"]
            
    # Clean up test cache files
    client.delete("/api/v1/semantic/cache")


def test_embedding_manager_singleton_behavior():
    """Verify EmbeddingManager lazily loads model and maintains singleton reference."""
    from app.modules.semantic.embedding_manager import EmbeddingManager
    m1 = EmbeddingManager.get_model()
    m2 = EmbeddingManager.get_model()
    assert m1 is m2
    assert EmbeddingManager.model_name == "all-MiniLM-L6-v2"


def test_candidate_encoder_direct():
    """Verify CandidateEncoder encodes candidate dictionaries into embeddings."""
    from app.modules.semantic.candidate_encoder import CandidateEncoder
    cand = {
        "current_title": "AI Engineer",
        "years_of_experience": 3.5,
        "skills_list": "Python, ML",
        "highest_education_tier": "tier_1",
        "raw_json": "{}"
    }
    embs = CandidateEncoder.encode_candidates([cand], batch_size=1)
    assert embs.shape == (1, 384)


def test_job_encoder_direct():
    """Verify JobEncoder encodes structured jobs details into embeddings."""
    from app.modules.semantic.job_encoder import JobEncoder
    job = {
        "title": "Data Scientist",
        "seniority": "Senior",
        "industry": "Technology",
        "required_skills": ["Python", "SQL"],
        "preferred_skills": ["Spark"],
        "soft_skills": ["Communication"],
        "raw_text": "Required Python, SQL. Nice to have Spark."
    }
    emb = JobEncoder.encode_job(job)
    assert emb.shape == (384,)


def test_similarity_engine_direct():
    """Verify SimilarityEngine calculates cosine similarity matches correctly."""
    from app.modules.semantic.similarity_engine import SimilarityEngine
    job_emb = np.array([1.0, 0.0], dtype=np.float32)
    cand_embs = np.array([
        [1.0, 0.0],
        [0.0, 1.0]
    ], dtype=np.float32)
    cids = ["C1", "C2"]
    
    matches = SimilarityEngine.compute_similarity(job_emb, cand_embs, cids)
    assert len(matches) == 2
    assert matches[0]["candidate_id"] == "C1"
    assert matches[0]["score"] == pytest.approx(100.0)
    assert matches[1]["candidate_id"] == "C2"
    assert matches[1]["score"] == pytest.approx(0.0)


def test_embedding_cache_direct():
    """Verify EmbeddingCache saves and retrieves active job embeddings successfully."""
    from app.modules.semantic.embedding_cache import EmbeddingCache
    job_id = "JOB_CACHE_TEST"
    job_emb = np.random.randn(384).astype(np.float32)
    job_emb = job_emb / np.linalg.norm(job_emb)
    
    # Save active job
    EmbeddingCache.save_job_embedding(job_id, job_emb)
    
    # Retrieve active job
    retrieved = EmbeddingCache.get_job_embedding(job_id)
    assert np.allclose(retrieved, job_emb)
    
    # Status check
    status = EmbeddingCache.get_status()
    assert status["has_active_job_vector"] is True
    assert status["active_job_id"] == job_id
    
    # Delete job
    EmbeddingCache.delete_job_cache(job_id)
    assert EmbeddingCache.get_job_embedding(job_id) is None

