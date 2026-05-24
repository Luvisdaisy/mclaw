import asyncio
import logging

import click

from mclaw.agents.graph import build_stage1_graph
from mclaw.agents.state import AgentState

logger = logging.getLogger(__name__)


@click.command()
@click.argument("query")
@click.pass_context
def plan(ctx: click.Context, query: str) -> None:
    """Plan a mod installation with dual-agent orchestration.

    Uses Planner and Executor agents via LangGraph to analyze
    mod installation requests for compatibility.
    """
    click.echo(f"Planning: {query}")

    state = AgentState(user_query=query, stage=1)
    graph = build_stage1_graph()

    click.echo("Running Planner → Executor graph...")
    result = asyncio.run(graph.ainvoke(state))

    state = _result_to_state(result)

    click.echo(f"\nTarget: Minecraft {state.target_mc_version} ({state.target_loader})")

    click.echo(f"\nTasks ({len(state.tasks)}):")
    for i, task in enumerate(state.tasks):
        status_icon = "✓" if task.status == "completed" else "✗" if task.status == "failed" else "○"
        click.echo(f"  {status_icon} {task.description}")
        if task.result:
            click.echo(f"    → {task.result}")

    if state.error:
        click.echo(f"\nError: {state.error}")


def _result_to_state(result: dict) -> AgentState:
    """Convert graph.ainvoke dict result back to AgentState."""
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
