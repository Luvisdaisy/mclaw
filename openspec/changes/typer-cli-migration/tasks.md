## 1. Dependencies

- [x] 1.1 Update `pyproject.toml` — replace `click` with `typer` and `rich` as direct dependencies, update entry point to `app`
- [x] 1.2 Run `uv sync` and verify typer + rich are installed

## 2. Core Commands Migration

- [x] 2.1 Migrate `src/mclaw/cli/diagnose_cmd.py` — remove click decorators, keep `run_diagnose` only, add Rich markup
- [x] 2.2 Migrate `src/mclaw/cli/plan_cmd.py` — remove click decorators, keep `run_plan` only, add Rich markup
- [x] 2.3 Migrate `src/mclaw/cli/solve_cmd.py` — remove click decorators, keep `run_solve` only, add Rich markup
- [x] 2.4 Migrate `src/mclaw/cli/monitor.py` — use `typer.Typer()` sub-app, Rich Console for output

## 3. Main Entry Point

- [x] 3.1 Rewrite `src/mclaw/cli/main.py` — use `typer.Typer(invoke_without_command=True)`, register commands via `@app.command()`, add monitor sub-typer
- [x] 3.2 Verify `mclaw --help` shows Rich-formatted output

## 4. Interactive Menu with Rich

- [x] 4.1 Enhance `src/mclaw/cli/menu.py` — use `rich.console.Console`, `rich.panel.Panel`, `rich.prompt.IntPrompt`, `rich.rule.Rule` for styled menu
- [x] 4.2 Update streaming callback to use `console.print()` with Rich markup for status indicators

## 5. Tests and Verification

- [x] 5.1 Run full test suite — no test changes needed, **42/42 pass**
- [x] 5.2 Verify `mclaw`, `mclaw diagnose`, `mclaw plan`, `mclaw solve`, `mclaw monitor --help` all function correctly with Rich output
