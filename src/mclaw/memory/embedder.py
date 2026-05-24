import logging

import httpx

from mclaw.llm.config import LLMConfig

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_EMBED_MODEL = "mxbai-embed-large"


async def get_embedding(text: str) -> list[float]:
    """Generate an embedding for crash log text.

    Uses Ollama's OpenAI-compatible embeddings API directly.
    """
    config = LLMConfig()

    if config.provider == "ollama":
        base_url = config.base_url or OLLAMA_BASE_URL
        return await _ollama_embed(text, base_url)

    base_url = config.base_url or "https://api.openai.com/v1"
    return await _openai_embed(text, base_url, config.api_key)


async def _ollama_embed(text: str, base_url: str) -> list[float]:
    """Call Ollama embeddings API."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/embeddings",
            json={"model": OLLAMA_EMBED_MODEL, "input": text},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]


async def _openai_embed(text: str, base_url: str, api_key: str) -> list[float]:
    """Call OpenAI embeddings API."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/embeddings",
            json={"model": "text-embedding-3-small", "input": text},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]
