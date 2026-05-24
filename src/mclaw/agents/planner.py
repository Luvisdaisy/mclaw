import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from mclaw.agents.state import AgentState, Task
from mclaw.llm.config import LLMConfig
from mclaw.llm.provider import create_llm, llm_invoke

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are a Minecraft modding expert. Your task is to analyze a mod installation request and generate a structured task plan.

## Available Tools
- query_mod: Search for mod information (name, versions, loaders, dependencies) via Modrinth/CurseForge
- check_compatibility: Check if a mod is compatible with target Minecraft version and loader
- check_dependencies: Verify that all required dependencies are available

## Output Format
Respond with a JSON object only:

{
  "target_mc_version": "1.20.1",
  "target_loader": "forge",
  "tasks": [
    {
      "description": "task description",
      "tool": "tool_name",
      "expected_output": "what this task should produce"
    }
  ]
}

## Rules
- Extract target Minecraft version and mod loader from the user query if mentioned
- Default to Minecraft 1.20.1 and Forge if not specified
- Break down the request into 2-5 specific, actionable tasks
- If the query is ambiguous, include a task to ask for clarification
"""


async def run_planner(state: AgentState) -> dict:
    """Parse user input and generate a structured task list."""
    config = LLMConfig()
    llm = create_llm(config)

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"User request: {state.user_query}"),
    ]

    response = await llm_invoke(llm, messages)
    raw = response.content

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = _extract_json(raw)

    state.target_mc_version = data.get("target_mc_version", "1.20.1")
    state.target_loader = data.get("target_loader", "forge")
    state.tasks = [Task(**t) for t in data.get("tasks", [])]
    state.current_task_index = 0
    state.done = False

    return {"tasks": state.tasks, "target_mc_version": state.target_mc_version, "target_loader": state.target_loader}


def _extract_json(text: str) -> dict:
    """Attempt to extract JSON from LLM response that may contain markdown fences."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse planner output: %s", text[:200])
        return {"tasks": []}
