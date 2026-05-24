import asyncio
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.rule import Rule


def show_menu(console: Console) -> int:
    """Display the interactive menu and return the user's choice (1-3)."""
    console.clear()
    console.print(
        Panel.fit(
            "[bold yellow]mclaw[/] — Minecraft Modpack Analysis Tool\n"
            "[dim]LLM-powered agent technology learning project[/]",
            border_style="yellow",
        )
    )
    console.print()
    console.print("  [bold cyan][1][/] Diagnose  — crash log analysis")
    console.print("  [bold cyan][2][/] Plan      — mod installation planning")
    console.print("  [bold cyan][3][/] Solve     — full analysis with diagnosis")
    console.print("  [bold cyan][0][/] Exit")
    console.print()

    while True:
        try:
            choice = IntPrompt.ask("  Enter choice", default=0, console=console)
            if choice in (0, 1, 2, 3):
                return choice
            console.print("[red]Please enter 0-3[/]")
        except (ValueError, KeyboardInterrupt):
            return 0


def prompt_crash_log_path(console: Console) -> str | None:
    """Prompt for a crash log file path with validation."""
    while True:
        try:
            path_str = Prompt.ask("  Crash log file path", default="", console=console)
            if not path_str:
                return None

            path = Path(path_str.strip())
            if path.exists() and path.is_file():
                return str(path)

            console.print(f"[red]File not found:[/] {path_str}")
        except (ValueError, KeyboardInterrupt):
            return None


def prompt_query(console: Console) -> str | None:
    """Prompt for a natural language query."""
    try:
        query = Prompt.ask("  What would you like to do?", default="", console=console)
        return query.strip() if query.strip() else None
    except (ValueError, KeyboardInterrupt):
        return None


def run_interactive(console: Console | None = None) -> None:
    """Main interactive loop — show menu, route to selected function."""
    if console is None:
        console = Console()

    choice = show_menu(console)

    if choice == 0:
        console.print("  Goodbye!")
        return

    if choice == 1:
        _run_diagnose_interactive(console)
    elif choice == 2:
        _run_plan_interactive(console)
    elif choice == 3:
        _run_solve_interactive(console)


def _run_diagnose_interactive(console: Console) -> None:
    """Interactive diagnose with streaming via Rich Console."""
    console.clear()
    console.print(Rule("[bold]Diagnose[/]", style="cyan"))
    console.print()

    path = prompt_crash_log_path(console)
    if not path:
        console.print("  Cancelled.")
        return

    from mclaw.cli.diagnose_cmd import run_diagnose
    asyncio.run(run_diagnose(crash_log=path, callback=console.print))


def _run_plan_interactive(console: Console) -> None:
    """Interactive plan with streaming via Rich Console."""
    console.clear()
    console.print(Rule("[bold]Plan[/]", style="cyan"))
    console.print()

    query = prompt_query(console)
    if not query:
        console.print("  Cancelled.")
        return

    from mclaw.cli.plan_cmd import run_plan
    asyncio.run(run_plan(query=query, callback=console.print))


def _run_solve_interactive(console: Console) -> None:
    """Interactive solve with streaming via Rich Console."""
    console.clear()
    console.print(Rule("[bold]Solve[/]", style="cyan"))
    console.print()

    query = prompt_query(console)
    if not query:
        console.print("  Cancelled.")
        return

    from mclaw.cli.solve_cmd import run_solve
    asyncio.run(run_solve(query=query, callback=console.print))
