from pathlib import Path

import click


def show_menu() -> int:
    """Display the interactive menu and return the user's choice (1-3)."""
    click.clear()
    click.echo("=" * 50)
    click.echo("  mclaw — Minecraft Modpack Analysis Tool")
    click.echo("=" * 50)
    click.echo()
    click.echo("  [1] Diagnose  — crash log analysis")
    click.echo("  [2] Plan      — mod installation planning")
    click.echo("  [3] Solve     — full analysis with diagnosis")
    click.echo("  [0] Exit")
    click.echo()

    while True:
        try:
            choice = click.prompt("  Enter choice", type=int, default=0)
            if choice in (0, 1, 2, 3):
                return choice
            click.echo("  Please enter 0-3")
        except click.Abort:
            return 0


def prompt_crash_log_path() -> str | None:
    """Prompt for a crash log file path with validation."""
    while True:
        try:
            path_str = click.prompt(
                "  Crash log file path",
                type=str,
                default="",
            )
            if not path_str:
                return None

            path = Path(path_str.strip())
            if path.exists() and path.is_file():
                return str(path)

            click.echo(f"  File not found: {path_str}")
        except click.Abort:
            return None


def prompt_query() -> str | None:
    """Prompt for a natural language query."""
    try:
        query = click.prompt(
            "  What would you like to do?",
            type=str,
            default="",
        )
        return query.strip() if query.strip() else None
    except click.Abort:
        return None


def run_interactive() -> None:
    """Main interactive loop — show menu, route to selected function."""
    choice = show_menu()

    if choice == 0:
        click.echo("  Goodbye!")
        return

    if choice == 1:
        _run_diagnose_interactive()
    elif choice == 2:
        _run_plan_interactive()
    elif choice == 3:
        _run_solve_interactive()


def _run_diagnose_interactive() -> None:
    """Interactive diagnose flow with streaming output."""
    click.clear()
    click.echo("--- Diagnose ---")
    click.echo()

    path = prompt_crash_log_path()
    if not path:
        click.echo("  Cancelled.")
        return

    from mclaw.cli.diagnose_cmd import run_diagnose
    import asyncio
    asyncio.run(run_diagnose(crash_log=path, callback=click.echo))


def _run_plan_interactive() -> None:
    """Interactive plan flow with streaming output."""
    click.clear()
    click.echo("--- Plan ---")
    click.echo()

    query = prompt_query()
    if not query:
        click.echo("  Cancelled.")
        return

    from mclaw.cli.plan_cmd import run_plan
    import asyncio
    asyncio.run(run_plan(query=query, callback=click.echo))


def _run_solve_interactive() -> None:
    """Interactive solve flow with streaming output."""
    click.clear()
    click.echo("--- Solve ---")
    click.echo()

    query = prompt_query()
    if not query:
        click.echo("  Cancelled.")
        return

    from mclaw.cli.solve_cmd import run_solve
    import asyncio
    asyncio.run(run_solve(query=query, callback=click.echo))
