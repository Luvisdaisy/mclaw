import logging
from pathlib import Path

import click
from langchain_core.messages import HumanMessage, SystemMessage

from mclaw.llm.config import LLMConfig
from mclaw.llm.provider import create_llm, llm_invoke
from mclaw.mc_platform.crash_parser import parse_crash_log
from mclaw.prompts.crash_diagnosis import CRASH_DIAGNOSIS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--crash-log", required=True, type=click.Path(exists=True),
    help="Path to crash log file",
)
@click.option(
    "--output", "-o", type=click.Path(), default=None,
    help="Save diagnosis result as JSON",
)
@click.pass_context
def diagnose(ctx: click.Context, crash_log: str, output: str | None) -> None:
    """Single-script crash diagnosis using one LLM call.

    Parses a Minecraft crash log and uses a single LLM call to
    classify the root cause into one of three categories:
    dependency_missing, version_conflict, or ecosystem_incompatible.
    """
    filepath = Path(crash_log)

    click.echo(f"Parsing crash log: {filepath.name}")
    parsed = parse_crash_log(filepath)
    click.echo(f"  Type: {parsed.crash_type or 'unknown'}")
    click.echo(f"  Referenced mods: {', '.join(parsed.referenced_mods) if parsed.referenced_mods else 'none'}")

    click.echo("Calling LLM for diagnosis...")
    config = LLMConfig()
    llm = create_llm(config)

    system_msg = SystemMessage(content=CRASH_DIAGNOSIS_SYSTEM_PROMPT)
    human_msg = HumanMessage(content=f"""Analyze this Minecraft crash log and output a JSON diagnosis.

Crash log:
```
{parsed.raw_text[:8000]}
```

Parsed info:
- Crash type: {parsed.crash_type or 'unknown'}
- Referenced mods: {', '.join(parsed.referenced_mods) if parsed.referenced_mods else 'none'}
- Error: {parsed.error_message or 'none'}
""")

    import asyncio
    response = asyncio.run(llm_invoke(llm, [system_msg, human_msg]))

    click.echo("\n--- Diagnosis Result ---")
    click.echo(response.content)

    if output:
        Path(output).write_text(response.content, encoding="utf-8")
        click.echo(f"\nResult saved to: {output}")
