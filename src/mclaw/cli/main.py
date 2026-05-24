import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from mclaw.cli.diagnose_cmd import run_diagnose
from mclaw.cli.menu import run_interactive
from mclaw.cli.monitor import monitor_app
from mclaw.cli.plan_cmd import run_plan
from mclaw.cli.solve_cmd import run_solve

app = typer.Typer(invoke_without_command=True)
console = Console()


@app.callback()
def main(ctx: typer.Context, stage: Annotated[int | None, typer.Option("--stage")] = None) -> None:
    """mclaw — Agent-driven Minecraft modpack analysis tool.

    Diagnose crashes, plan mod installations, and analyze compatibility
    using LLM-powered agents.

    Run without arguments to enter interactive menu.
    """
    ctx.ensure_object(dict)
    ctx.obj["stage"] = stage

    if ctx.invoked_subcommand is None:
        run_interactive(console)


@app.command()
def diagnose(
    crash_log: Annotated[Path, typer.Option(exists=True, help="Path to crash log file")],
    output: Annotated[str | None, typer.Option("--output", "-o", help="Save diagnosis result as JSON")] = None,
) -> None:
    """Single-script crash diagnosis using one LLM call."""
    asyncio.run(run_diagnose(crash_log=str(crash_log), callback=console.print, output=output))


@app.command()
def plan(query: Annotated[str, typer.Argument(help="Natural language query")]) -> None:
    """Plan a mod installation with dual-agent orchestration."""
    asyncio.run(run_plan(query=query, callback=console.print))


@app.command()
def solve(query: Annotated[str, typer.Argument(help="Natural language query")]) -> None:
    """Full agent orchestration with Planner, Executor, and Diagnoser."""
    asyncio.run(run_solve(query=query, callback=console.print))


app.add_typer(monitor_app)
