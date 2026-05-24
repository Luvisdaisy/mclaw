import json
import logging
from datetime import datetime, timezone

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "crash_cases"


class MemoryStore:
    """ChromaDB-backed store for crash case history."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        self.client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(anonymized_telemetry=False),
        )
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.collection = self.client.get_collection(COLLECTION_NAME)
        except Exception:
            self.collection = self.client.create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "Minecraft crash case history"},
            )

    def store_case(
        self,
        case_id: str,
        crash_text: str,
        embedding: list[float],
        diagnosis: dict,
    ) -> None:
        """Store a diagnosed crash case with its embedding and metadata."""
        self.collection.add(
            ids=[case_id],
            embeddings=[embedding],
            documents=[crash_text],
            metadatas=[{
                "category": diagnosis.get("category", "unknown"),
                "confidence": diagnosis.get("confidence", 0.0),
                "summary": diagnosis.get("summary", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }],
        )
        logger.info("Stored crash case: %s", case_id)

    def clear(self) -> None:
        """Remove all stored cases."""
        try:
            self.client.delete_collection(COLLECTION_NAME)
            self._ensure_collection()
        except Exception:
            pass
