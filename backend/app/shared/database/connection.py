import sqlite3
from contextlib import contextmanager
from pathlib import Path
from loguru import logger
from app.shared.config.settings import settings

# Parse the database URL from settings
# default setting is "sqlite:///./aura.db"
def get_db_path() -> Path:
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        # Remove sqlite:/// prefix
        path_str = db_url.replace("sqlite:///", "")
        path = Path(path_str)
        if not path.is_absolute():
            # Resolve relative to the backend root directory (contains app/)
            backend_root = Path(__file__).resolve().parent.parent.parent.parent
            return (backend_root / path).absolute()
        return path.absolute()
    
    backend_root = Path(__file__).resolve().parent.parent.parent.parent
    return (backend_root / "aura.db").absolute()


@contextmanager
def get_db_connection():
    """Context manager to obtain a SQLite database connection."""
    db_path = get_db_path()
    # Ensure parent directories exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    
    try:
        # Enable WAL mode for better concurrency and write speed
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys=ON;")
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("Database transaction rolled back due to error: {e}", e=str(e))
        raise
    finally:
        conn.close()
