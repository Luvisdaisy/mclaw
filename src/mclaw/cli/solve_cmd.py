import asyncio
import logging
from collections.abc import Callable

import click

from mclaw.agents.graph import build_stage2_graph
from mclaw.agents.state import AgentState
from mclaw.cli.plan_cmd import _result_to_state

logger = logging.getLogger(__name__)


async def run_solve(
    query: str,
    callback: Callable[[str], None] | None = None,
) -> str:
    """Run full agent orchestration, streaming progress via callback."""
    _emit(callback, f"Solving: {query}")

    state = AgentState(user_query=query, stage=2)
    graph = build_stage2_graph()

    _emit(callback, "Running Planner -> Executor -> Diagnoser graph...")
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

    if state.diagnosis:
        d = state.diagnosis
        _emit(callback, f"\nDiagnosis:")
        _emit(callback, f"  Category: {d.get('category', 'unknown')}")
        _emit(callback, f"  Confidence: {d.get('confidence', 0.0)}")
        _emit(callback, f"  Summary: {d.get('summary', 'N/A')}")
        if d.get("suspicious_mods"):
            _emit(callback, f"  Suspicious mods: {', '.join(d['suspicious_mods'])}")
        if d.get("fix_suggestion"):
            _emit(callback, f"  Fix: {d['fix_suggestion']}")

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
    if state.diagnosis:
        lines.append(f"Diagnosis: {state.diagnosis.get('category')}")
    return "\n".join(lines)


@click.command()
@click.argument("query")
@click.pass_context
def solve(ctx: click.Context, query: str) -> None:
    """Full agent orchestration with Planner, Executor, and Diagnoser."""
    asyncio.run(run_solve(query=query, callback=click.echo))
