import asyncio
import logging
from collections.abc import Callable

import click

from mclaw.agents.graph import build_stage1_graph
from mclaw.agents.state import AgentState

logger = logging.getLogger(__name__)


async def run_plan(
    query: str,
    callback: Callable[[str], None] | None = None,
) -> str:
    """Run mod installation planning, streaming progress via callback."""
    _emit(callback, f"Planning: {query}")

    state = AgentState(user_query=query, stage=1)
    graph = build_stage1_graph()

    _emit(callback, "Running Planner -> Executor graph...")
    _emit(callback, "  [Planner] Analyzing request...")
    result = await graph.ainvoke(state)

    state = _result_to_state(result)

    _emit(callback, f"\nTarget: Minecraft {state.target_mc_version} ({state.target_loader})")

    _emit(callback, f"\nTasks ({len(state.tasks)}):")
    for i, task in enumerate(state.tasks):
        status_icon = "v" if task.status == "completed" else "x" if task.status == "failed" else "o"
        _emit(callback, f"  [{status_icon}] {task.description}")
        if task.result:
            _emit(callback, f"      -> {task.result}")

    if state.error:
        _emit(callback, f"\nError: {state.error}")

    return _format_summary(state)


def _emit(callback: Callable[[str], None] | None, msg: str) -> None:
    if callback:
        callback(msg)


def _format_summary(state: AgentState) -> str:
    lines = [f"Target: {state.target_mc_version} ({state.target_loader})"]
    for t in state.tasks:
        lines.append(f"  [{t.status}] {t.description}")
    return "\n".join(lines)


def _result_to_state(result: dict) -> AgentState:
    if isinstance(result, AgentState):
        return result
    state = AgentState()
    state.tasks = result.get("tasks", [])
    state.target_mc_version = result.get("target_mc_version", "")
    state.target_loader = result.get("target_loader", "")
    state.compatibility_results = result.get("compatibility_results", [])
    state.error = result.get("error", "")
    state.done = result.get("done", False)
    state.diagnosis = result.get("diagnosis")
    state.current_task_index = result.get("current_task_index", 0)
    return state


@click.command()
@click.argument("query")
@click.pass_context
def plan(ctx: click.Context, query: str) -> None:
    """Plan a mod installation with dual-agent orchestration."""
    asyncio.run(run_plan(query=query, callback=click.echo))
