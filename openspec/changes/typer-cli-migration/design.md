## Context

当前 CLI 架构：`main.py` 用 click 的 `@click.group(invoke_without_command=True)` 作为入口，各命令模块用 `@click.command()` 和 `@click.option()` / `@click.argument()` 定义。交互菜单用 `click.echo` + `click.prompt` 实现数字选择。

typer 是 click 的上层封装，通过 Python 类型注解自动生成 CLI 接口。Rich 是终端富文本库，typer 原生支持 Rich 集成（`typer.rich_utils`）。

## Goals / Non-Goals

**Goals:**
- 所有 CLI 命令从 click 装饰器迁移到 typer 装饰器
- 交互菜单使用 Rich 的 Panel / Rule / 彩色文本增强
- Help 输出自动格式化，带颜色和分组
- 流式输出使用 Rich markup 标记状态（`[green]...[/]`）
- 命令名、参数名、行为完全向后兼容

**Non-Goals:**
- 不改变 agent / mc_platform / llm / memory 层
- 不添加 typer 的高级功能（progress bar, shell completion 文件生成）
- 不移除 `click` 包本身（typer 内部依赖它）

## Decisions

### 1. typer.Typer 替代 click.group

typer 的 `app = typer.Typer()` 直接替代 `@click.group()`。`app.command()` 替代 `main.add_command()`。

无参数时的菜单行为通过设置 `invoke_without_command=True` 并检查 `ctx.invoked_subcommand` 实现——typer 完全兼容 click context。

### 2. 类型注解驱动参数定义

typer 的核心优势是参数类型从 Python 类型注解推断：
```python
# Before (click)
@click.option("--crash-log", type=click.Path(exists=True))

# After (typer)
def diagnose(crash_log: Annotated[Path, typer.Option(exists=True)])
```

这消除了 click 的 `type=` 样板代码，同时保持完全相同的验证行为。

### 3. 使用 click 原生保留 `invoke_without_command`

typer 不支持直接的 `invoke_without_command` 参数，需要用回调处理。由于 typer 本质是 click 的包装，可以在 `Typer.callback()` 装饰的函数中通过 `click.Context` 检查 `invoked_subcommand`。

### 4. Rich Console 替代 click.echo 做流式输出

```python
from rich.console import Console
console = Console()

# callback 传入 console.print
callback = lambda msg: console.print(msg, markup=True)
```

支持 `[bold]`, `[green]`, `[dim]` 等 Rich markup 标记。

### 5. 入口点保持 `mclaw.cli.main:main`

typer 的 `typer.Typer` 实例可直接作为 click 的 `click.Group` 使用。pyproject.toml 的 `[project.scripts]` 入口点指向 typer app 实例：`mclaw = "mclaw.cli.main:app"`

## Risks / Trade-offs

- **typer/Rich 版本兼容** → pin 版本，typer 0.15+ 与现有依赖树兼容
- **Windows 终端颜色支持** → Rich 自动检测终端能力并降级，Windows Terminal / PowerShell 均良好支持
- **Help 输出格式变化** → typer 默认 help 风格不同但信息更丰富，不影响脚本解析（用 `--help` 获取帮助文本而非解析其格式）
