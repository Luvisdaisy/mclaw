import asyncio

import pytest
import tenacity

from mclaw.llm.config import LLMConfig
from mclaw.llm.retry import is_retryable_status, with_retry


class TestLLMConfig:

    def test_defaults(self):
        config = LLMConfig()
        assert config.provider == "ollama"
        assert config.model == "qwen3:4b"
        assert config.timeout == 60
        assert config.max_retries == 3

    def test_timeout_parsing(self, monkeypatch):
        monkeypatch.setenv("MCLAW_LLM_TIMEOUT", "30")
        config = LLMConfig()
        assert config.timeout == 30

    def test_max_retries_parsing(self, monkeypatch):
        monkeypatch.setenv("MCLAW_LLM_MAX_RETRIES", "5")
        config = LLMConfig()
        assert config.max_retries == 5


class TestRetryableStatus:

    def test_retryable_codes(self):
        assert is_retryable_status(429)
        assert is_retryable_status(502)
        assert is_retryable_status(503)
        assert is_retryable_status(504)

    def test_non_retryable_codes(self):
        assert not is_retryable_status(400)
        assert not is_retryable_status(401)
        assert not is_retryable_status(404)
        assert not is_retryable_status(500)


class TestRetryDecorator:

    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self):
        call_count = 0

        @with_retry(max_attempts=3, timeout=5.0)
        async def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await succeed()
        assert result == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.05, timeout=5.0)
        async def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("transient failure")
            return "recovered"

        result = await flaky()
        assert result == "recovered"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_raises(self):
        @with_retry(max_attempts=2, timeout=0.05)
        async def slow():
            await asyncio.sleep(1.0)
            return "never"

        with pytest.raises(tenacity.RetryError) as exc_info:
            await slow()
        assert isinstance(exc_info.value.last_attempt.exception(), TimeoutError)

    @pytest.mark.asyncio
    async def test_exhausts_retries(self):
        @with_retry(max_attempts=2, min_wait=0.01, max_wait=0.05, timeout=5.0)
        async def always_fails():
            raise ConnectionError("persistent failure")

        with pytest.raises(tenacity.RetryError) as exc_info:
            await always_fails()
        assert isinstance(exc_info.value.last_attempt.exception(), ConnectionError)
