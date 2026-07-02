import json
from typing import Dict, Any, Tuple, List
from app.modules.features.base_engine import BaseFeatureEngine

class CertificationEngine(BaseFeatureEngine):
    """
    Certification Intelligence Engine.
    Evaluates cloud, AI/ML, DevOps, database/big-data, security, and programming certificates.
    Scored based on relevance and count (up to 100 max).
    """

    def _run_calculation(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        raw_json_str = candidate.get("raw_json")
        
        cert_list: List[Dict[str, Any]] = []
        if raw_json_str:
            try:
                raw_data = json.loads(raw_json_str)
                cert_list = raw_data.get("certifications", [])
            except Exception:
                pass
                
        # If they don't have any certifications, return 0 score
        if not cert_list:
            return 0.0, {"certifications_found": [], "categories_matched": []}
            
        matched_categories = set()
        cased_cert_names = []
        
        for cert in cert_list:
            name = cert.get("name", "").strip()
            name_lower = name.lower()
            cased_cert_names.append(name)
            
            # 1. Cloud
            if any(k in name_lower for k in ["aws", "amazon", "gcp", "google cloud", "azure", "cloud architect"]):
                matched_categories.add("Cloud")
            # 2. AI/ML
            elif any(k in name_lower for k in ["tensorflow", "pytorch", "deep learning", "machine learning", "artificial intelligence", "nvidia"]):
                matched_categories.add("AI/ML")
            # 3. DevOps
            elif any(k in name_lower for k in ["docker", "kubernetes", "cka", "ckad", "jenkins", "terraform", "ansible", "devops"]):
                matched_categories.add("DevOps")
            # 4. Data / Databases
            elif any(k in name_lower for k in ["spark", "databricks", "snowflake", "big data", "hadoop", "oracle", "mongodb", "mysql", "sql"]):
                matched_categories.add("Data")
            # 5. Security
            elif any(k in name_lower for k in ["cissp", "ceh", "security+", "cism", "comptia", "cybersecurity"]):
                matched_categories.add("Security")
            # 6. Programming / General
            elif any(k in name_lower for k in ["python", "java", "c++", "scrum", "agile", "pmp"]):
                matched_categories.add("Programming/Agile")
            else:
                matched_categories.add("General Professional")
                
        # Score calculation:
        # Each certification adds 25 points, capped at 100 points
        score = min(100.0, len(cert_list) * 25.0)
        
        # Give a small extra boost for having multiple distinct categories
        category_bonus = len(matched_categories) * 5.0
        score = min(100.0, score + category_bonus)
        
        metadata = {
            "certifications_found": cased_cert_names,
            "categories_matched": sorted(list(matched_categories)),
            "total_certifications": len(cert_list)
        }
        
        return score, metadata
