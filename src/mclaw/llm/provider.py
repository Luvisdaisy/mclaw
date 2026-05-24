import logging
from collections.abc import AsyncIterator
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from mclaw.llm.config import LLMConfig
from mclaw.llm.retry import is_retryable_status, with_retry

logger = logging.getLogger(__name__)


def create_llm(config: LLMConfig | None = None) -> BaseChatModel:
    """Create an LLM instance based on configuration.

    Supports OpenAI-compatible APIs and Ollama.
    """
    if config is None:
        config = LLMConfig()

    provider = config.provider.lower()

    if provider == "ollama":
        base_url = config.base_url or "http://localhost:11434/v1"
        return ChatOpenAI(
            model=config.model,
            base_url=base_url,
            api_key="ollama",
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    base_url = config.base_url
    api_key = config.api_key

    return ChatOpenAI(
        model=config.model,
        base_url=base_url,
        api_key=api_key,
        timeout=config.timeout,
        max_retries=config.max_retries,
    )


@with_retry()
async def llm_invoke(
    llm: BaseChatModel,
    messages: list[BaseMessage],
) -> BaseMessage:
    """Invoke an LLM with retry and timeout handling."""
    return await llm.ainvoke(messages)


@with_retry()
async def llm_stream(
    llm: BaseChatModel,
    messages: list[BaseMessage],
) -> AsyncIterator[Any]:
    """Stream LLM response with retry and timeout handling.

    Note: retry on stream errors may result in duplicate tokens.
    """
    async for chunk in llm.astream(messages):
        yield chunk
