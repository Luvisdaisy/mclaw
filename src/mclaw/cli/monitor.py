import logging
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from mclaw.mc_platform.crash_parser import parse_crash_log

logger = logging.getLogger(__name__)
console = Console()

monitor_app = typer.Typer(
    name="monitor",
    help="Monitor — Watch crash reports directory for automatic diagnosis.",
)


@monitor_app.command()
def watch(
    path: Annotated[str | None, typer.Option("--path")] = None,
    interval: Annotated[int, typer.Option("--interval")] = 5,
) -> None:
    """Watch crash reports directory for new crash files."""
    watch_path = _resolve_watch_path(path)

    if not watch_path.exists():
        console.print(f"[yellow]Warning:[/] {watch_path} does not exist. Waiting for it...")

    console.print(f"Watching: {watch_path}")
    console.print(f"Polling interval: {interval}s")
    console.print("Press Ctrl+C to stop.\n")

    known_files: set[str] = set()

    try:
        while True:
            if watch_path.exists():
                for entry in watch_path.iterdir():
                    if entry.is_file() and entry.name not in known_files:
                        if entry.suffix in (".txt", ".log"):
                            known_files.add(entry.name)
                            _handle_new_crash(entry)
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\nMonitor stopped.")


def _resolve_watch_path(path: str | None) -> Path:
    if path:
        return Path(path)

    import platform

    home = Path.home()
    if platform.system() == "Windows":
        appdata = Path.home() / "AppData" / "Roaming"
        return appdata / ".minecraft" / "crash-reports"
    else:
        return home / "Library" / "Application Support" / "minecraft" / "crash-reports"


def _handle_new_crash(filepath: Path) -> None:
    console.print(f"\n[[bold]{time.strftime('%H:%M:%S')}[/]] New crash: {filepath.name}")

    try:
        parsed = parse_crash_log(filepath)
        console.print(f"  Type: {parsed.crash_type or 'unknown'}")
        console.print(f"  Error: {parsed.error_message or parsed.description}")
        if parsed.referenced_mods:
            console.print(f"  Mods: {', '.join(parsed.referenced_mods)}")
    except Exception as e:
        console.print(f"  [red]Parse error:[/] {e}")
