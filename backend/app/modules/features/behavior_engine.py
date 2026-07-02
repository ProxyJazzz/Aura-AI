from typing import Dict, Any, Tuple
from app.modules.features.base_engine import BaseFeatureEngine

class BehaviorEngine(BaseFeatureEngine):
    """
    Behavior Intelligence Engine.
    Evaluates:
    1. Availability (Open-to-work flag) (Max 25 points)
    2. Career Stability & Job Switching Frequency (Average tenure) (Max 25 points)
    3. Recruiter Engagement Rate (Response Rate) (Max 25 points)
    4. Responsiveness Speed (Average Response Time in Hours) (Max 25 points)
    """

    def _run_calculation(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        # 1. Availability (Max 25 points)
        open_to_work = bool(candidate.get("open_to_work_flag") or False)
        availability_points = 25.0 if open_to_work else 10.0  # Still active, but not active-seeking
        
        # 2. Career Stability (Max 25 points)
        avg_tenure = float(candidate.get("avg_tenure_months") or 0.0)
        if avg_tenure >= 24.0:
            stability_points = 25.0
        elif avg_tenure >= 12.0:
            stability_points = 15.0
        else:
            stability_points = 0.0  # Job hopper penalty
            
        # 3. Recruiter Response Rate (Max 25 points)
        response_rate = float(candidate.get("recruiter_response_rate") or 0.8) # Default 80% fallback
        response_rate_points = response_rate * 25.0
        
        # 4. Responsiveness Speed (Max 25 points)
        response_time = float(candidate.get("avg_response_time_hours") or 24.0) # Default 24 hours fallback
        if response_time <= 2.0:
            speed_points = 25.0
        elif response_time <= 12.0:
            speed_points = 20.0
        elif response_time <= 24.0:
            speed_points = 15.0
        else:
            speed_points = 5.0
            
        # Sum final score
        final_score = availability_points + stability_points + response_rate_points + speed_points
        
        metadata = {
            "open_to_work": open_to_work,
            "average_tenure_months": avg_tenure,
            "recruiter_response_rate": response_rate,
            "avg_response_time_hours": response_time,
            "availability_score": availability_points,
            "stability_score": stability_points,
            "responsiveness_rate_score": response_rate_points,
            "responsiveness_speed_score": speed_points
        }
        
        return final_score, metadata
