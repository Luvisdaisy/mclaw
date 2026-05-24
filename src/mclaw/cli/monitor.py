import logging
import time
from pathlib import Path

import click

from mclaw.mc_platform.crash_parser import parse_crash_log

logger = logging.getLogger(__name__)


@click.group()
def monitor_cmd() -> None:
    """Monitor — Watch crash reports directory for automatic diagnosis."""


@monitor_cmd.command()
@click.option(
    "--path", type=click.Path(), default=None,
    help="Crash reports directory (auto-detected if omitted)",
)
@click.option("--interval", type=int, default=5, help="Polling interval in seconds")
@click.pass_context
def watch(ctx: click.Context, path: str | None, interval: int) -> None:
    """Watch crash reports directory for new crash files."""
    watch_path = _resolve_watch_path(path)

    if not watch_path.exists():
        click.echo(f"Warning: {watch_path} does not exist. Waiting for it...")

    click.echo(f"Watching: {watch_path}")
    click.echo(f"Polling interval: {interval}s")
    click.echo("Press Ctrl+C to stop.\n")

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
        click.echo("\nMonitor stopped.")


def _resolve_watch_path(path: str | None) -> Path:
    """Resolve the crash reports directory for the current platform."""
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
    """Process a newly detected crash report."""
    click.echo(f"\n[{time.strftime('%H:%M:%S')}] New crash: {filepath.name}")

    try:
        parsed = parse_crash_log(filepath)
        click.echo(f"  Type: {parsed.crash_type or 'unknown'}")
        click.echo(f"  Error: {parsed.error_message or parsed.description}")
        if parsed.referenced_mods:
            click.echo(f"  Mods: {', '.join(parsed.referenced_mods)}")
    except Exception as e:
        click.echo(f"  Parse error: {e}")
