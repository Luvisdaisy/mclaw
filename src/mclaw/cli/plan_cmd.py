import asyncio
import logging
from collections.abc import Callable

from mclaw.agents.graph import build_stage1_graph
from mclaw.agents.state import AgentState

logger = logging.getLogger(__name__)


async def run_plan(
    query: str,
    callback: Callable[[str], None] | None = None,
) -> str:
    """Run mod installation planning, streaming progress via callback."""
    _emit(callback, f"[bold]Planning:[/] {query}")

    state = AgentState(user_query=query, stage=1)
    graph = build_stage1_graph()

    _emit(callback, "[bold]Running Planner -> Executor graph...[/]")
    _emit(callback, "  [dim][Planner] Analyzing request...[/]")
    result = await graph.ainvoke(state)

    state = _result_to_state(result)

    _emit(callback, f"\n[bold]Target:[/] Minecraft {state.target_mc_version} ({state.target_loader})")

    _emit(callback, f"\n[bold]Tasks ({len(state.tasks)}):[/]")
    for i, task in enumerate(state.tasks):
        if task.status == "completed":
            icon = "[green]v[/]"
        elif task.status == "failed":
            icon = "[red]x[/]"
        else:
            icon = "[dim]o[/]"
        _emit(callback, f"  {icon} {task.description}")
        if task.result:
            _emit(callback, f"      -> {task.result}")

    if state.error:
        _emit(callback, f"\n[bold red]Error:[/] {state.error}")

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
