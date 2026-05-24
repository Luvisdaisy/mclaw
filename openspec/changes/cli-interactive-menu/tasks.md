## 1. Menu Entry Point

- [x] 1.1 Create `src/mclaw/cli/menu.py` — implement `show_menu()` with numbered function list, user input, choice routing
- [x] 1.2 Implement parameter prompts — `prompt_crash_log_path()` and `prompt_query()` with validation
- [x] 1.3 Modify `src/mclaw/cli/main.py` — no subcommand invokes `run_interactive()`, direct commands still route normally

## 2. Streaming Output

- [x] 2.1 Refactor `src/mclaw/cli/diagnose_cmd.py` — extract `run_diagnose(crash_log, callback)` with streaming progress
- [x] 2.2 Refactor `src/mclaw/cli/plan_cmd.py` — extract `run_plan(query, callback)` streaming per task status
- [x] 2.3 Refactor `src/mclaw/cli/solve_cmd.py` — extract `run_solve(query, callback)` streaming per agent transition
- [x] 2.4 Wire menu interactive flows to pass `click.echo` as callback for step-by-step streaming

## 3. Testing and Verification

- [x] 3.1 Add `tests/test_menu.py` — 9 tests covering callback collection, null callback, output file, menu routing, parameter prompts
- [x] 3.2 Verify `mclaw` bare invocation shows the interactive menu
- [x] 3.3 Verify `mclaw diagnose/plan/solve` direct commands still execute normally
