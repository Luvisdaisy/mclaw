from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    description: str
    tool: str = ""
    expected_output: str = ""
    status: str = "pending"
    result: Any = None


@dataclass
class AgentState:
    """Shared state for the LangGraph agent runtime."""

    user_query: str = ""
    target_mc_version: str = ""
    target_loader: str = ""

    tasks: list[Task] = field(default_factory=list)
    current_task_index: int = 0

    mod_info_cache: dict[str, dict] = field(default_factory=dict)
    compatibility_results: list[dict] = field(default_factory=list)

    error: str = ""
    stage: int = 1

    diagnosis: dict | None = None
    memory_hits: list[dict] = field(default_factory=list)

    done: bool = False
