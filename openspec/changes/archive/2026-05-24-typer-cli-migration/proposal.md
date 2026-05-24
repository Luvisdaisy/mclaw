## Why

当前 CLI 使用 click 构建，虽然功能完整但终端输出缺乏视觉层次——所有文字同色、无进度指示、help 信息单调。typer 基于 click 并深度集成 Rich 库，可零成本获得彩色输出、自动格式化的帮助页面、进度条、shell 补全等现代 CLI 体验，且与现有 click 生态完全兼容。typer 已在依赖树中（langchain 等间接依赖），只需显式声明即可。

## What Changes

- **New**: 添加 `typer` 和 `rich` 为直接依赖
- **Modified**: 所有 CLI 模块从 click 装饰器迁移到 typer 装饰器，保持命令名和参数不变
- **Modified**: 交互菜单使用 Rich 的 `Panel`、`Rule`、彩色文本增强视觉效果
- **Modified**: 流式输出使用 Rich 的 `Console` 和状态标记（`[bold green]v[/]` 等）
- **Modified**: pyproject.toml 中 `[project.scripts]` 入口点适配 typer app
- **Removed**: `click` 从直接依赖中移除（typer 内部依赖 click，无需显式声明）

## Capabilities

### New Capabilities

<!-- Typer 迁移是 UI 框架替换，不引入新的功能 capability -->

### Modified Capabilities

- `cli-interactive`: 交互菜单和命令行入口由 click 实现改为 typer + Rich 实现，功能行为不变但视觉表现增强

## Impact

- 6 个 CLI 文件重构: `main.py`, `diagnose_cmd.py`, `plan_cmd.py`, `solve_cmd.py`, `monitor.py`, `menu.py`
- `pyproject.toml`: click → typer 依赖替换，`[project.scripts]` 入口更新
- 不改变 agent、mc_platform、llm、memory 层
- 命令名和行为完全向后兼容
