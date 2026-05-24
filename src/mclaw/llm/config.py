import os
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    provider: str = field(default_factory=lambda: os.getenv("MCLAW_LLM_PROVIDER", "ollama"))
    api_key: str = field(default_factory=lambda: os.getenv("MCLAW_LLM_API_KEY", ""))
    base_url: str | None = field(default_factory=lambda: os.getenv("MCLAW_LLM_BASE_URL"))
    model: str = field(default_factory=lambda: os.getenv("MCLAW_LLM_MODEL", "qwen3:4b"))
    timeout: int = field(default_factory=lambda: int(os.getenv("MCLAW_LLM_TIMEOUT", "60")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("MCLAW_LLM_MAX_RETRIES", "3")))
