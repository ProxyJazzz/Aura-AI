from typing import Optional, Dict, Any


class JobCache:
    """In-memory cache for the currently active structured Hiring Profile."""

    _active_profile: Optional[Dict[str, Any]] = None

    @classmethod
    def get_active_profile(cls) -> Optional[Dict[str, Any]]:
        return cls._active_profile

    @classmethod
    def set_active_profile(cls, profile: Dict[str, Any]) -> None:
        cls._active_profile = profile

    @classmethod
    def clear(cls) -> None:
        cls._active_profile = None
