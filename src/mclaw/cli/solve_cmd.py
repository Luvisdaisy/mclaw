import asyncio
import logging

import click

from mclaw.agents.graph import build_stage2_graph
from mclaw.agents.state import AgentState
from mclaw.cli.plan_cmd import _result_to_state

logger = logging.getLogger(__name__)


@click.command()
@click.argument("query")
@click.pass_context
def solve(ctx: click.Context, query: str) -> None:
    """Full agent orchestration with Planner, Executor, and Diagnoser.

    All three agents active with conditional routing —
    failures trigger automatic crash diagnosis.
    """
    click.echo(f"Solving: {query}")

    state = AgentState(user_query=query, stage=2)
    graph = build_stage2_graph()

    click.echo("Running Planner → Executor → Diagnoser graph...")
    result = asyncio.run(graph.ainvoke(state))

    state = _result_to_state(result)

    click.echo(f"\nTarget: Minecraft {state.target_mc_version} ({state.target_loader})")

    click.echo(f"\nTasks ({len(state.tasks)}):")
    for i, task in enumerate(state.tasks):
        status_icon = "✓" if task.status == "completed" else "✗" if task.status == "failed" else "○"
        click.echo(f"  {status_icon} {task.description}")
        if task.result:
            click.echo(f"    → {task.result}")

    if state.diagnosis:
        d = state.diagnosis
        click.echo(f"\nDiagnosis:")
        click.echo(f"  Category: {d.get('category', 'unknown')}")
        click.echo(f"  Confidence: {d.get('confidence', 0.0)}")
        click.echo(f"  Summary: {d.get('summary', 'N/A')}")
        if d.get("suspicious_mods"):
            click.echo(f"  Suspicious mods: {', '.join(d['suspicious_mods'])}")
        if d.get("fix_suggestion"):
            click.echo(f"  Fix: {d['fix_suggestion']}")

    if state.error:
        click.echo(f"\nError: {state.error}")
