## Context

当前菜单用 `IntPrompt.ask()` 接收数字选择。这意味着：
- 用户必须按数字键然后回车，无法用方向键预览
- 选项数量多时难以记忆编号
- 与 `select`/`fzf` 等主流终端交互模式不一致

通过 `prompt_toolkit` 的 `RadioList` 或手动监听方向键实现可视化选择菜单。

## Goals / Non-Goals

**Goals:**
- 方向键 ↑/↓ 在选项间移动，高亮当前选项
- Enter 确认当前高亮选项
- 跨平台支持（macOS / Windows / Linux）
- 与现有的 Rich Console 样式集成（保留 Panel、颜色、markup）

**Non-Goals:**
- 不实现搜索/过滤功能（后续可加）
- 不改变参数输入阶段（仍用 Rich Prompt）
- 不改变直接命令调用行为

## Decisions

### 1. 使用 prompt_toolkit 的 `RadioList` 而非自制方向键监听

prompt_toolkit 内置了 `RadioList` dialog 组件，提供开箱即用的方向键导航和可视焦点切换，且跨平台处理终端原始模式。自制方案需要手动处理 `termios`（类Unix）和 `msvcrt`（Windows），增加了维护成本。

### 2. RadioList 风格与 Rich 保持一致

`RadioList` 的默认样式可以通过 `formatted_text` 自定义。使用 Rich 的 `Console` 输入 `prompt_toolkit` 的 `HTML` 格式化来复用已有的颜色和样式，避免两套风格。

### 3. 通过 `create_prompt_toolkit_application` 集成到现有流程

不改变 `run_interactive()` 的调用链——`show_menu()` 返回值保持为 `int`（1-3），只是内部实现从 `IntPrompt.ask()` 改为 `RadioList.run()`。

### 4. prompt_toolkit 只用于菜单选择，参数输入保持 Rich Prompt

Rich 的 `IntPrompt` / `Prompt` 对文本输入已足够好用，不需要为参数输入增加 prompt_toolkit 的复杂会话管理。

## Risks / Trade-offs

- **prompt_toolkit 增加依赖体积** → 广泛使用的标准库，与 ipython、jupyter 等共享依赖，通常已在虚拟环境中
- **Windows CMD 可能存在渲染差异** → prompt_toolkit 原生支持 Windows Console API，已处理此问题
- **RadioList 选择后屏幕不干净** → 选择后立即 `print()` 选项确认或 `console.clear()` 进入下一阶段
