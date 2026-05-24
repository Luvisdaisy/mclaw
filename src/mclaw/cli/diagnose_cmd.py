import logging
from collections.abc import Callable
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from mclaw.llm.config import LLMConfig
from mclaw.llm.provider import create_llm, llm_invoke
from mclaw.mc_platform.crash_parser import parse_crash_log
from mclaw.prompts.crash_diagnosis import CRASH_DIAGNOSIS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def run_diagnose(
    crash_log: str,
    callback: Callable[[str], None] | None = None,
    output: str | None = None,
) -> str:
    """Run crash diagnosis, streaming progress via callback if provided."""
    filepath = Path(crash_log)

    _emit(callback, f"[bold]Parsing crash log:[/] {filepath.name}")
    parsed = parse_crash_log(filepath)
    _emit(callback, f"  Type: {parsed.crash_type or 'unknown'}")
    _emit(callback, f"  Referenced mods: {', '.join(parsed.referenced_mods) if parsed.referenced_mods else 'none'}")

    _emit(callback, "[bold]Calling LLM for diagnosis...[/]")
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

    response = await llm_invoke(llm, [system_msg, human_msg])

    _emit(callback, "\n[bold]--- Diagnosis Result ---[/]")
    _emit(callback, response.content)

    if output:
        Path(output).write_text(response.content, encoding="utf-8")
        _emit(callback, f"\nResult saved to: {output}")

    return response.content


def _emit(callback: Callable[[str], None] | None, msg: str) -> None:
    if callback:
        callback(msg)
