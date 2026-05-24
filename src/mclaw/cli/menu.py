import asyncio
from pathlib import Path

from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.prompt import Prompt
from rich.rule import Rule


DIALOG_STYLE = Style.from_dict({
    "dialog": "bg:#1a1a2e",
    "dialog frame-label": "bg:#ffffff #000000",
    "dialog.body": "bg:#1a1a2e #ffffff",
    "radio-list": "#ffffff",
    "radio-list.selected": "bg:#00afff #ffffff",
    "dialog.title": "bg:#ffd700 #000000",
})


def show_menu() -> str | None:
    """Display an interactive menu with arrow key navigation."""
    result = radiolist_dialog(
        title="mclaw — Minecraft Modpack Analysis Tool",
        text="Select a function (use arrows to move, Enter to confirm):",
        values=[
            ("diagnose", "Diagnose  — crash log analysis"),
            ("plan",     "Plan      — mod installation planning"),
            ("solve",    "Solve     — full analysis with diagnosis"),
        ],
        style=DIALOG_STYLE,
    ).run()

    return result


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

    choice = show_menu()

    if choice is None or choice == "exit":
        console.print("  Goodbye!")
        return

    if choice == "diagnose":
        _run_diagnose_interactive(console)
    elif choice == "plan":
        _run_plan_interactive(console)
    elif choice == "solve":
        _run_solve_interactive(console)


def _run_diagnose_interactive(console: Console) -> None:
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
    console.clear()
    console.print(Rule("[bold]Solve[/]", style="cyan"))
    console.print()

    query = prompt_query(console)
    if not query:
        console.print("  Cancelled.")
        return

    from mclaw.cli.solve_cmd import run_solve
    asyncio.run(run_solve(query=query, callback=console.print))
