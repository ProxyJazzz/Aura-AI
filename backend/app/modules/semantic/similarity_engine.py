from typing import List, Dict, Any
import numpy as np


class SimilarityEngine:
    """Computes cosine similarity match metrics between job and candidate embeddings."""

    @staticmethod
    def compute_similarity(
        job_emb: np.ndarray,
        candidate_embs: np.ndarray,
        candidate_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Compute cosine similarity (dot product of normalized embeddings) between the active job
        and all candidate vectors. Returns a list of semantic match dicts normalized to 0-100.
        """
        if candidate_embs.size == 0 or len(candidate_ids) == 0:
            return []

        # Perform fast vector dot product similarity: shape (num_candidates,)
        # Both arrays are expected to be unit-normalized
        scores = np.dot(candidate_embs, job_emb)
        
        matches = []
        for cid, score in zip(candidate_ids, scores):
            # Normalize to 0-100 range
            normalized_score = float(max(0.0, score) * 100.0)
            matches.append({
                "candidate_id": cid,
                "score": normalized_score
            })
            
        return matches
