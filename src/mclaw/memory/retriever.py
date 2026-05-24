import logging

from mclaw.memory.store import MemoryStore

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.65
TOP_K = 3


class CaseRetriever:
    """Semantic search over stored crash cases."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def find_similar(
        self,
        embedding: list[float],
        threshold: float = SIMILARITY_THRESHOLD,
        top_k: int = TOP_K,
    ) -> list[dict]:
        """Find top-K similar crash cases above the similarity threshold."""
        try:
            results = self.store.collection.query(
                query_embeddings=[embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.warning("ChromaDB query failed: %s", e)
            return []

        hits: list[dict] = []
        if not results["ids"] or not results["ids"][0]:
            return hits

        for i, case_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i]
            similarity = 1.0 - distance

            if similarity >= threshold:
                hits.append({
                    "case_id": case_id,
                    "similarity": similarity,
                    "diagnosis": results["metadatas"][0][i],
                    "crash_text": results["documents"][0][i],
                })

        return hits
