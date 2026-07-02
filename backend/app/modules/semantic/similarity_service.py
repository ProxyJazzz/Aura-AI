import numpy as np
from typing import List, Tuple
from loguru import logger

class SimilarityService:
    """Calculates dot product similarities and ranks vector results."""

    @staticmethod
    def compute_scores(embeddings_matrix: np.ndarray, job_embedding: np.ndarray) -> np.ndarray:
        """
        Compute normalized cosine similarity scores.
        Since vectors are unit-normalized, cosine similarity is exactly the dot product.
        We convert it to a 0-100 percentage score.
        """
        # Ensure correct shapes
        if len(job_embedding.shape) == 1:
            job_emb = job_embedding
        else:
            job_emb = job_embedding.squeeze()
            
        logger.debug("Computing dot product over matrix of shape {shape}", shape=embeddings_matrix.shape)
        # Dot product: shape (N,)
        similarities = np.dot(embeddings_matrix, job_emb)
        # Clip just in case of float precision issues
        similarities = np.clip(similarities, -1.0, 1.0)
        
        # Convert [-1.0, 1.0] similarities to [0.0, 100.0] scores
        # We can map it directly: score = max(0.0, similarities) * 100.0
        scores = np.maximum(0.0, similarities) * 100.0
        return scores

    @staticmethod
    def rank_candidates(scores: np.ndarray, candidate_ids: List[str], top_k: int = 100) -> List[Tuple[str, float]]:
        """
        Sort candidate vectors and return Top-K matches with their scores.
        Uses argpartition for O(N) performance, which is much faster than full sorting.
        """
        num_candidates = len(scores)
        k = min(top_k, num_candidates)
        if k <= 0:
            return []
            
        # Argpartition gets the top-k indices (unordered)
        if k < num_candidates:
            # Indices of the top k items
            top_k_indices = np.argpartition(scores, -k)[-k:]
            # Sort only the top k items by score descending
            sorted_top_indices = top_k_indices[np.argsort(-scores[top_k_indices])]
        else:
            sorted_top_indices = np.argsort(-scores)
            
        ranked_results = [
            (candidate_ids[idx], float(scores[idx]))
            for idx in sorted_top_indices
        ]
        return ranked_results
