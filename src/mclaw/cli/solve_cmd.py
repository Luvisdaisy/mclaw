import asyncio
import logging
from collections.abc import Callable

from mclaw.agents.graph import build_stage2_graph
from mclaw.agents.state import AgentState
from mclaw.cli.plan_cmd import _result_to_state

logger = logging.getLogger(__name__)


async def run_solve(
    query: str,
    callback: Callable[[str], None] | None = None,
) -> str:
    """Run full agent orchestration, streaming progress via callback."""
    _emit(callback, f"[bold]Solving:[/] {query}")

    state = AgentState(user_query=query, stage=2)
    graph = build_stage2_graph()

    _emit(callback, "[bold]Running Planner -> Executor -> Diagnoser graph...[/]")
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

    if state.diagnosis:
        d = state.diagnosis
        _emit(callback, f"\n[bold]Diagnosis:[/]")
        _emit(callback, f"  Category: {d.get('category', 'unknown')}")
        _emit(callback, f"  Confidence: {d.get('confidence', 0.0)}")
        _emit(callback, f"  Summary: {d.get('summary', 'N/A')}")
        if d.get("suspicious_mods"):
            _emit(callback, f"  Suspicious mods: {', '.join(d['suspicious_mods'])}")
        if d.get("fix_suggestion"):
            _emit(callback, f"  Fix: {d['fix_suggestion']}")

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
    if state.diagnosis:
        lines.append(f"Diagnosis: {state.diagnosis.get('category')}")
    return "\n".join(lines)
