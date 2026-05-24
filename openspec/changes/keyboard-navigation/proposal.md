## Why

当前交互菜单通过输入数字选择功能（`[1] Diagnose`），体验上与主流 CLI 工具的设计预期不符。用户期望用方向键在选项间移动、回车确认选择。增加键盘导航后交互更直觉、使用门槛更低。

## What Changes

- **New**: 添加 `prompt_toolkit` 依赖，用于跨平台的键盘事件处理（方向键）和原始终端模式
- **Modified**: `show_menu()` 从数字输入改为基础方向键导航：光标高亮当前选项，↑/↓ 移动，Enter 确认
- **Modified**: 功能选择和参数输入阶段拆分：菜单选功能 → 引导输入参数（参数输入仍用 Rich Prompt 保持简单）

## Capabilities

### New Capabilities

- `keyboard-nav`: 交互式菜单方向键导航，提供跨平台的终端键盘事件处理

### Modified Capabilities

- `cli-interactive`: 菜单选择方式从数字输入改为方向键导航，参数输入阶段和行为不变

## Impact

- 新增依赖：`prompt_toolkit` ≥ 3.0
- 修改 `src/mclaw/cli/menu.py` — 重写 `show_menu()` 为方向键导航
- 修改 `openspec/changes/keyboard-navigation/specs/cli-interactive/spec.md` — 更新菜单选择规格
- 不改变 `main.py`、命令模块或 agent 核心
