## Why

当前 CLI 必须记住并输入完整命令（`mclaw diagnose --crash-log <path>` 等），启动门槛高且输出是一次性的，看不到 agent 内部的思考过程。需要一个交互式菜单让用户在终端内选择功能，并通过流式输出展示 agent 运行过程，提升使用体验和可观测性。

## What Changes

- **New**: `mclaw` 无参数启动时进入交互式选择菜单，用方向键选择 diagnose / plan / solve
- **New**: diagnose 模式下提示用户拖入或输入崩溃日志路径
- **New**: plan / solve 模式下提示用户输入自然语言 query
- **New**: 执行过程中流式输出 agent 的规划、工具调用、步骤结果，而非等待最后一次性打印
- **Modified**: 原有的直接命令调用（`mclaw diagnose --crash-log`、`mclaw plan`、`mclaw solve`）保持不变，作为快速/脚本调用入口

## Capabilities

### New Capabilities

- `cli-interactive`: 终端交互式菜单，提供功能选择和参数输入引导，执行过程中流式输出 agent 运行状态

### Modified Capabilities

<!-- 无已有 capability 的 spec 级别变更 -->

## Impact

- 新增 `src/mclaw/cli/menu.py` — 交互式菜单入口
- 修改 `src/mclaw/cli/main.py` — 无参数时调用 menu
- 修改 `src/mclaw/cli/diagnose_cmd.py`、`plan_cmd.py`、`solve_cmd.py` — 增加流式回调/生成器模式，供 menu 和直接调用共用
- 新增依赖：无需额外包，使用 Python 内置 `input` + 简单的 ANSI 控制即可，或复用 click 的 prompt 能力
