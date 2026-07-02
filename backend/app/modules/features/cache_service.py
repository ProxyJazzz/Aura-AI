import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime

class FeatureCacheService:
    """Manages the disk persistence and statistics of candidate feature scorecard profiles."""

    @staticmethod
    def get_backend_root() -> Path:
        """Resolve absolute path to the backend directory."""
        return Path(__file__).resolve().parent.parent.parent.parent

    @classmethod
    def get_cache_path(cls) -> Path:
        """Get the absolute path to feature_profiles.json."""
        return cls.get_backend_root() / "feature_profiles.json"

    @classmethod
    def save_cache(cls, profiles: Dict[str, Dict[str, Any]]):
        """Save candidate feature profiles dictionary to disk as JSON."""
        cache_path = cls.get_cache_path()
        logger.info("Saving {count} candidate feature profiles to disk cache: {file}...", 
                    count=len(profiles), file=cache_path.name)
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
            logger.info("Feature profiles cache saved successfully.")
        except Exception as e:
            logger.error("Error writing feature cache file: {err}", err=str(e))
            raise

    @classmethod
    def load_cache(cls) -> Dict[str, Dict[str, Any]]:
        """Load candidate feature profiles dictionary from disk."""
        cache_path = cls.get_cache_path()
        if not cache_path.exists():
            raise FileNotFoundError("Feature profiles cache file does not exist.")
            
        logger.info("Loading feature profiles from disk cache...")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error reading feature cache file: {err}", err=str(e))
            raise

    @classmethod
    def clear_cache(cls):
        """Delete feature profiles cache from disk."""
        cache_path = cls.get_cache_path()
        if cache_path.exists():
            try:
                os.remove(cache_path)
                logger.info("Feature profiles cache file deleted successfully.")
            except Exception as e:
                logger.error("Error deleting feature cache file: {err}", err=str(e))
                raise
        else:
            logger.info("Feature profiles cache is already empty.")

    @classmethod
    def get_cache_status(cls) -> Dict[str, Any]:
        """Compile file system statistics for the feature profiles cache."""
        cache_path = cls.get_cache_path()
        
        is_built = cache_path.exists()
        total_profiles = 0
        file_size_mb = 0.0
        last_modified = None
        
        if is_built:
            try:
                # Load JSON to get exact record count
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    total_profiles = len(data)
                
                # Get file size in MB
                file_size_bytes = cache_path.stat().st_size
                file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
                
                # Get modified timestamp
                mtime = cache_path.stat().st_mtime
                last_modified = datetime.fromtimestamp(mtime).isoformat() + "Z"
            except Exception as e:
                logger.warning("Error compiling feature cache status: {err}", err=str(e))
                is_built = False
                
        return {
            "is_built": is_built,
            "total_profiles": total_profiles,
            "cache_file_size_mb": file_size_mb,
            "last_modified": last_modified
        }
