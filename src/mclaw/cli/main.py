import click

from mclaw.cli.diagnose_cmd import diagnose
from mclaw.cli.menu import run_interactive
from mclaw.cli.monitor import monitor_cmd
from mclaw.cli.plan_cmd import plan
from mclaw.cli.solve_cmd import solve


@click.group(invoke_without_command=True)
@click.option("--stage", type=int, default=None, help="Override execution stage")
@click.pass_context
def main(ctx: click.Context, stage: int | None) -> None:
    """mclaw — Agent-driven Minecraft modpack analysis tool.

    Diagnose crashes, plan mod installations, and analyze compatibility
    using LLM-powered agents.

    Run without arguments to enter interactive menu.
    """
    ctx.ensure_object(dict)
    ctx.obj["stage"] = stage

    if ctx.invoked_subcommand is None:
        run_interactive()


main.add_command(diagnose)
main.add_command(plan)
main.add_command(solve)
main.add_command(monitor_cmd, name="monitor")
