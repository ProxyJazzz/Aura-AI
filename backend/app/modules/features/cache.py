from typing import Dict, Any, Optional
from app.modules.features.cache_service import FeatureCacheService
from app.modules.features.repository import FeatureRepository


class FeatureCache:
    """Manages memory, file, and database persistence layers for Candidate Feature scorecard profiles."""

    _cached_profiles: Optional[Dict[str, Dict[str, Any]]] = None

    @classmethod
    def load_profiles(cls, force: bool = False) -> Dict[str, Dict[str, Any]]:
        """Load candidate feature scorecards from memory, file cache, or database."""
        if force or cls._cached_profiles is None:
            # Try to load from SQLite first
            profiles = FeatureRepository.get_all_feature_profiles()
            if not profiles:
                # Fallback to json file cache
                try:
                    profiles = FeatureCacheService.load_cache()
                    # Backpopulate SQLite
                    FeatureRepository.save_feature_profiles_batch(list(profiles.values()))
                except FileNotFoundError:
                    profiles = {}
            cls._cached_profiles = profiles
        return cls._cached_profiles

    @classmethod
    def save_profiles(cls, profiles: Dict[str, Dict[str, Any]]) -> None:
        """Persists candidate feature scorecards across all caching layers."""
        cls._cached_profiles = profiles
        # Save to disk file cache
        FeatureCacheService.save_cache(profiles)
        # Save to SQLite database
        FeatureRepository.save_feature_profiles_batch(list(profiles.values()))

    @classmethod
    def clear(cls) -> None:
        """Wipes memory, files, and database cache records."""
        cls._cached_profiles = None
        FeatureCacheService.clear_cache()
        FeatureRepository.clear_feature_profiles()

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Fetch cache statistics."""
        status = FeatureCacheService.get_cache_status()
        # Verify db counts
        db_profiles = FeatureRepository.get_all_feature_profiles()
        if db_profiles:
            status["is_built"] = True
            status["total_profiles"] = len(db_profiles)
        return status
