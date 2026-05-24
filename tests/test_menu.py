import asyncio

import pytest

from mclaw.cli.menu import prompt_crash_log_path, prompt_query, show_menu


class TestMenuRouting:

    def test_show_menu_is_callable(self):
        """show_menu exists and is callable (interactive test requires terminal)."""
        assert callable(show_menu)


class TestParameterPrompts:

    def test_prompt_query_is_callable(self):
        """prompt_query exists and is callable."""
        assert callable(prompt_query)

    def test_prompt_crash_log_path_is_callable(self):
        """prompt_crash_log_path exists and is callable."""
        assert callable(prompt_crash_log_path)


class TestDiagnoseCallback:

    @pytest.mark.asyncio
    async def test_callback_receives_messages(self):
        """run_diagnose sends progress messages via callback."""
        from mclaw.cli.diagnose_cmd import run_diagnose

        messages: list[str] = []

        def collect(msg: str) -> None:
            messages.append(msg)

        fixture = "tests/fixtures/crash_logs/dependency_missing_jei.txt"
        result = await run_diagnose(crash_log=fixture, callback=collect)

        assert len(messages) > 0, "Should have emitted progress messages"
        assert any("Parsing" in m for m in messages), "Should show parsing step"
        assert any("LLM" in m or "Diagnosis" in m for m in messages), "Should show LLM or result step"

    @pytest.mark.asyncio
    async def test_no_callback_works(self):
        """run_diagnose works without a callback."""
        from mclaw.cli.diagnose_cmd import run_diagnose

        fixture = "tests/fixtures/crash_logs/dependency_missing_jei.txt"
        result = await run_diagnose(crash_log=fixture, callback=None)
        assert result, "Should return diagnosis text"

    @pytest.mark.asyncio
    async def test_output_file_saved(self, tmp_path):
        """run_diagnose saves output to file when path provided."""
        from mclaw.cli.diagnose_cmd import run_diagnose

        outfile = tmp_path / "result.json"
        fixture = "tests/fixtures/crash_logs/dependency_missing_jei.txt"
        await run_diagnose(crash_log=fixture, callback=None, output=str(outfile))
        assert outfile.exists(), "Output file should be created"


class TestPlanCallback:

    @pytest.mark.asyncio
    async def test_callback_receives_messages(self):
        """run_plan sends progress messages via callback."""
        from mclaw.cli.plan_cmd import run_plan

        messages: list[str] = []

        def collect(msg: str) -> None:
            messages.append(msg)

        result = await run_plan(query="Install Create for 1.20.1 Forge", callback=collect)

        assert len(messages) > 0, "Should have emitted progress messages"
        assert any("Planning" in m for m in messages), "Should show planning step"
        assert any("Planner" in m for m in messages), "Should show planner step"
        assert any("Task" in m or "v" in m or "x" in m or "o" in m for m in messages), "Should show task results"

    @pytest.mark.asyncio
    async def test_no_callback_works(self):
        """run_plan works without a callback."""
        from mclaw.cli.plan_cmd import run_plan

        result = await run_plan(query="Install Create for 1.20.1 Forge", callback=None)
        assert result, "Should return summary text"


class TestSolveCallback:

    @pytest.mark.asyncio
    async def test_callback_receives_messages(self):
        """run_solve sends progress messages via callback."""
        from mclaw.cli.solve_cmd import run_solve

        messages: list[str] = []

        def collect(msg: str) -> None:
            messages.append(msg)

        result = await run_solve(query="Install Create for 1.20.1 Forge", callback=collect)

        assert len(messages) > 0, "Should have emitted progress messages"
        assert any("Solving" in m for m in messages), "Should show solving step"
