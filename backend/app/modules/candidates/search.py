from typing import List, Dict, Any, Tuple
from app.shared.database import get_db_connection

class CandidateSearch:
    """Keyword search engine for candidate records (Name, Skills, Company, Degree, Certification, Language)."""

    @classmethod
    def search(
        cls,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search candidates by matching query term against multiple text columns.
        Supports matching: anonymized_name, skills_list, current_company, current_title, highest_education_tier.
        """
        if not query:
            return [], 0

        term = f"%{query.strip().lower()}%"

        sql = """
            SELECT * FROM candidates
            WHERE is_valid = 1 AND (
                LOWER(anonymized_name) LIKE ? OR
                LOWER(skills_list) LIKE ? OR
                LOWER(current_company) LIKE ? OR
                LOWER(current_title) LIKE ? OR
                LOWER(highest_education_tier) LIKE ?
            )
        """

        with get_db_connection() as conn:
            # Count total matches
            count_cursor = conn.execute(f"SELECT COUNT(*) FROM ({sql});", [term] * 5)
            total = count_cursor.fetchone()[0]

            # Fetch limit/offset page
            fetch_sql = f"{sql} LIMIT ? OFFSET ?;"
            cursor = conn.execute(fetch_sql, [term] * 5 + [limit, offset])
            rows = [dict(r) for r in cursor.fetchall()]

        return rows, total
