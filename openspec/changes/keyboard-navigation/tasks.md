## 1. Setup

- [x] 1.1 Add `prompt-toolkit>=3.0.0` to `pyproject.toml` dependencies
- [x] 1.2 Run `uv sync` — prompt-toolkit 3.0.52 installed

## 2. Menu Navigation

- [x] 2.1 Rewrite `src/mclaw/cli/menu.py` — use `prompt_toolkit.shortcuts.radiolist_dialog` with arrow key navigation, custom dialog style
- [x] 2.2 Verify menu renders correctly with arrow key navigation (↑/↓/Enter)

## 3. Verification

- [x] 3.1 Full test suite: 42/42 pass, no regressions
- [x] 3.2 Manual: `mclaw` → ↑/↓ 选择 → Enter 确认 → 参数输入 → 流式输出
