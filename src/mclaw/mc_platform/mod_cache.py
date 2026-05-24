import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_TTL = 24 * 60 * 60  # 24 hours in seconds
DEFAULT_CACHE_PATH = Path("data/mod_cache.db")


@dataclass
class CacheEntry:
    source: str
    mod_id: str
    data: dict
    last_updated: float


class ModCache:
    """SQLite-based mod metadata cache with TTL invalidation."""

    def __init__(self, db_path: str | Path = DEFAULT_CACHE_PATH, ttl: int = DEFAULT_TTL):
        self.db_path = Path(db_path)
        self.ttl = ttl
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mod_cache (
                    source TEXT NOT NULL,
                    mod_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    last_updated REAL NOT NULL,
                    PRIMARY KEY (source, mod_id)
                )
                """
            )
            conn.commit()

    def get(self, source: str, mod_id: str, force_refresh: bool = False) -> dict | None:
        """Get mod metadata from cache. Returns None if not found, stale, or force_refresh."""
        if force_refresh:
            return None

        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT data, last_updated FROM mod_cache WHERE source = ? AND mod_id = ?",
                (source, mod_id),
            ).fetchone()

        if row is None:
            return None

        data_str, last_updated = row
        now = time.time()
        age = now - last_updated

        if age > self.ttl:
            logger.info("Cache stale for %s/%s (age: %.1fh)", source, mod_id, age / 3600)
            return None

        return json.loads(data_str)

    def put(self, source: str, mod_id: str, data: dict) -> None:
        """Store mod metadata in cache."""
        now = time.time()
        data_str = json.dumps(data)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO mod_cache (source, mod_id, data, last_updated)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(source, mod_id) DO UPDATE SET
                    data = excluded.data,
                    last_updated = excluded.last_updated
                """,
                (source, mod_id, data_str, now),
            )
            conn.commit()

    def get_cache_age(self, source: str, mod_id: str) -> float | None:
        """Return the age of a cache entry in hours, or None if not cached."""
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT last_updated FROM mod_cache WHERE source = ? AND mod_id = ?",
                (source, mod_id),
            ).fetchone()

        if row is None:
            return None

        return (time.time() - row[0]) / 3600

    def clear(self) -> None:
        """Clear all cached entries."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("DELETE FROM mod_cache")
            conn.commit()
