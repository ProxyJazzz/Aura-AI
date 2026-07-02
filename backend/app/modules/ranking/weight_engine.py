from pathlib import Path
from typing import Dict
import yaml
from loguru import logger
from app.modules.ranking.exceptions import InvalidWeightProfileError

class WeightEngine:
    """Loads and validates weight configurations for candidate ranking."""

    DEFAULT_WEIGHTS = {
        "semantic": 25.0,
        "skills": 20.0,
        "experience": 15.0,
        "education": 10.0,
        "behavior": 10.0,
        "certification": 10.0,
        "language": 10.0,
    }

    @classmethod
    def load_weights(cls, profile_name: str) -> Dict[str, float]:
        """
        Load weights for the given profile from app/config/profiles.yaml.
        Validates that weights sum to exactly 100%.
        """
        backend_root = Path(__file__).resolve().parent.parent.parent.parent
        yaml_path = backend_root / "app" / "config" / "profiles.yaml"
        
        if not yaml_path.exists():
            logger.warning(f"profiles.yaml not found at {yaml_path}. Using default weights.")
            return cls.DEFAULT_WEIGHTS.copy()

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        profiles = data.get("profiles", {})
        if profile_name not in profiles:
            logger.warning(f"Weight profile '{profile_name}' not found. Falling back to 'generic'.")
            profile_name = "generic"
            
        weights_raw = profiles.get(profile_name, {})
        
        weights = {}
        for k in cls.DEFAULT_WEIGHTS.keys():
            weights[k] = float(weights_raw.get(k, 0.0))
            
        total_weight = sum(weights.values())
        if abs(total_weight - 100.0) > 0.01:
            raise InvalidWeightProfileError(f"Weights for profile '{profile_name}' must sum to 100, got {total_weight}")

        return weights
