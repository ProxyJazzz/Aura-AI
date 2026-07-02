import os
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
import numpy as np
from loguru import logger
from datetime import datetime

class CacheService:
    """Manages the disk persistence of candidate embeddings and candidate ID list mapping."""

    @staticmethod
    def get_backend_root() -> Path:
        """Resolve absolute path to the backend directory."""
        return Path(__file__).resolve().parent.parent.parent.parent

    @classmethod
    def get_embeddings_path(cls) -> Path:
        """Get the absolute path to candidate_embeddings.npy."""
        return cls.get_backend_root() / "candidate_embeddings.npy"

    @classmethod
    def get_ids_path(cls) -> Path:
        """Get the absolute path to candidate_ids.txt."""
        return cls.get_backend_root() / "candidate_ids.txt"

    @classmethod
    def save_cache(cls, embeddings: np.ndarray, candidate_ids: List[str]):
        """Save vector array and ID mapping files to disk."""
        npy_path = cls.get_embeddings_path()
        txt_path = cls.get_ids_path()
        
        # Guard to ensure arrays match in dimension
        if len(embeddings) != len(candidate_ids):
            raise ValueError(f"Size mismatch: {len(embeddings)} vectors, {len(candidate_ids)} IDs.")
            
        logger.info("Saving embedding vectors to {npy} and mapping IDs to {txt}...", npy=npy_path.name, txt=txt_path.name)
        try:
            # 1. Save binary matrix
            np.save(str(npy_path), embeddings)
            # 2. Save flat IDs list
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(candidate_ids))
            logger.info("Cache saved successfully. Total elements: {count}", count=len(candidate_ids))
        except Exception as e:
            logger.error("Error writing cache files: {err}", err=str(e))
            raise

    @classmethod
    def load_cache(cls) -> Tuple[np.ndarray, List[str]]:
        """Load vector matrix and candidate IDs from disk."""
        npy_path = cls.get_embeddings_path()
        txt_path = cls.get_ids_path()
        
        if not npy_path.exists() or not txt_path.exists():
            raise FileNotFoundError("Candidate embedding cache files do not exist.")
            
        logger.info("Loading semantic vector cache from disk...")
        try:
            embeddings = np.load(str(npy_path))
            with open(txt_path, "r", encoding="utf-8") as f:
                candidate_ids = [line.strip() for line in f if line.strip()]
                
            if len(embeddings) != len(candidate_ids):
                raise ValueError("Corruption detected: cache files have mismatched sizes.")
                
            return embeddings, candidate_ids
        except Exception as e:
            logger.error("Error loading cache files: {err}", err=str(e))
            raise

    @classmethod
    def clear_cache(cls):
        """Remove cache files from disk."""
        npy_path = cls.get_embeddings_path()
        txt_path = cls.get_ids_path()
        
        deleted = False
        try:
            if npy_path.exists():
                os.remove(npy_path)
                deleted = True
            if txt_path.exists():
                os.remove(txt_path)
                deleted = True
                
            if deleted:
                logger.info("Candidate embedding cache cleared successfully.")
            else:
                logger.info("Cache is already empty.")
        except Exception as e:
            logger.error("Error clearing cache: {err}", err=str(e))
            raise

    @classmethod
    def get_cache_status(cls) -> Dict[str, Any]:
        """Compile file system statistics for the vector embedding cache."""
        npy_path = cls.get_embeddings_path()
        txt_path = cls.get_ids_path()
        
        is_built = npy_path.exists() and txt_path.exists()
        total_embeddings = 0
        file_size_mb = 0.0
        last_modified = None
        
        if is_built:
            try:
                # Get vector counts by reading IDs file
                with open(txt_path, "r", encoding="utf-8") as f:
                    total_embeddings = sum(1 for line in f if line.strip())
                
                # Get file size in MB
                file_size_bytes = npy_path.stat().st_size
                file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
                
                # Get modified timestamp
                mtime = npy_path.stat().st_mtime
                last_modified = datetime.fromtimestamp(mtime).isoformat() + "Z"
            except Exception as e:
                logger.warning("Error compiling cache status: {err}", err=str(e))
                is_built = False
                
        return {
            "is_built": is_built,
            "total_embeddings": total_embeddings,
            "cache_file_size_mb": file_size_mb,
            "last_modified": last_modified,
            "model_name": "all-MiniLM-L6-v2"
        }
