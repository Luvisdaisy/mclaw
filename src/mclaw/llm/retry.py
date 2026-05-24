import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

import tenacity

logger = logging.getLogger(__name__)

T = TypeVar("T")


def with_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0,
    timeout: float = 60.0,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator for async LLM calls with exponential backoff and timeout."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:

        @tenacity.retry(
            wait=tenacity.wait_exponential(min=min_wait, max=max_wait),
            stop=tenacity.stop_after_attempt(max_attempts),
            retry=tenacity.retry_if_exception_type(
                (ConnectionError, TimeoutError, OSError)
            ),
            before_sleep=lambda retry_state: logger.warning(
                "Retry %d/%d after %.1fs: %s",
                retry_state.attempt_number,
                max_attempts,
                retry_state.idle_for,
                retry_state.outcome.exception() if retry_state.outcome else None,
            ),
        )
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            async with asyncio.timeout(timeout):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def is_retryable_status(status_code: int) -> bool:
    """Check if an HTTP status code warrants a retry."""
    return status_code in (429, 502, 503, 504)
