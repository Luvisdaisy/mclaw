## Context

当前 mclaw CLI 有两种交互模式：子命令模式（`mclaw diagnose`）和 `mclaw` 无参数时显示 help。用户必须记得完整命令和参数才能使用。此外所有命令都是先执行完毕再一次性输出，看不到 agent 内部的规划、工具调用等中间过程。

目标：`mclaw` 无参数启动时进入一个简单的终端菜单，用户用方向键或数字选择功能 → 引导输入参数 → 流式输出 agent 运行过程。原有的直接命令调用保持不变。

## Goals / Non-Goals

**Goals:**
- 无参数 `mclaw` 启动交互式菜单，列出 diagnose / plan / solve 三个功能
- 菜单支持方向键/数字选择
- 选择后交互式引导输入必要参数（崩溃日志路径或 query 文本）
- 执行过程中流式输出：规划任务列表、工具调用及结果、步骤推进
- 原有命令调用不受影响

**Non-Goals:**
- 不做 TUI 框架重写（不用 Textual、Rich layout）
- 不改为 Web UI 或 GUI
- 不改变 agent 图的核心逻辑

## Decisions

### 1. 使用 click 的 prompt 能力 + 简单菜单循环，不引入额外 UI 库

click 已内建 `click.prompt()`、`click.echo()`，加上 Python 的 ANSI 终端控制即可实现简洁的菜单选择。Textual 或 prompt_toolkit 虽然更强大，但引入额外依赖增加学习项目的复杂度，不符合 "了解底层机制" 的目标。

### 2. 菜单用数字键选择，非方向键

实现简单且兼容所有终端（Windows cmd / PowerShell / macOS Terminal / VS Code terminal）。方向键需要 termios/tty 原始模式控制，在不同平台上行为不一致。

```
  [1] Diagnose — 诊断 Minecraft 崩溃日志
  [2] Plan — 规划 mod 安装兼容性分析
  [3] Solve — 全流程分析（含自动诊断）

  Enter choice (1-3):
```

### 3. 流式输出通过 callback 模式实现

现有 `diagnose_cmd.py`、`plan_cmd.py`、`solve_cmd.py` 中的函数接受一个可选的 `stream_callback` 参数，agent 执行过程中调用 `callback("message")`。菜单模式下传入 `click.echo` 作为 callback 实现流式输出；直接命令模式不传 callback 保持原有行为。

### 4. 菜单入口整合进 main.py

`main()` 无参数时调用 `show_menu()`，有子命令时正常路由到对应命令。两套交互方式共用一个底层实现。

### 5. 暂不引入异步流式 tokens

流式输出是指 "步骤级别的流式输出"（正在规划...→ 规划完成 → 正在查询 Create → 查询完成），而非 LLM token 级别的流式输出。LLM token streaming 可作为后续增强。

## Risks / Trade-offs

- **数字选择不如方向键直观** → 菜单只有 3 项，数字足够简单；方向键可后续升级
- **流式输出增加代码复杂度** → callback 模式侵入性低，只在 agent 执行函数中加几处 `if callback: callback(...)` 即可
- **Windows cmd 中文/Emoji 显示** → 避免使用 emoji，输出使用纯文本状态标记
