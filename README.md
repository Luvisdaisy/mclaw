# mclaw

Agent technology learning project using Minecraft modpack building as a practice domain.

## Prerequisites

- **Python 3.12+** — [Download](https://www.python.org/downloads/)
- **uv** — Python package manager, [install](https://docs.astral.sh/uv/getting-started/installation/)
- **Docker Desktop** — For ChromaDB service, [Download](https://www.docker.com/products/docker-desktop/)

## Quick Start

### 1. 安装依赖

```bash
git clone git@github.com:Luvisdaisy/mclaw.git && cd mclaw
uv sync
```

### 2. 启动 Ollama（LLM 服务）

mclaw 默认使用本地 Ollama 运行 `qwen3:4b` 模型。

```bash
# 安装 Ollama: https://ollama.com
ollama serve              # 启动服务（如未运行）
ollama pull qwen3:4b      # 拉取对话模型
ollama pull mxbai-embed-large  # 拉取 embedding 模型（内存系统需要）
```

验证：
```bash
ollama list
# 应看到 qwen3:4b 和 mxbai-embed-large
```

### 3. 启动 ChromaDB（可选，内存系统需要）

```bash
uv run poe infra-up       # docker compose up -d
# ChromaDB 运行在 localhost:8000
```

### 4. 使用

```bash
# 诊断崩溃日志
uv run mclaw diagnose --crash-log tests/fixtures/crash_logs/dependency_missing_create.txt

# 规划 mod 安装（Planner + Executor）
uv run mclaw plan "Install Create mod for 1.20.1 Forge"

# 全流程诊断（Planner → Executor → Diagnoser）
uv run mclaw solve "Install Create mod for 1.20.1 Forge"

# 监听崩溃报告目录
uv run mclaw monitor watch
```

### 5. 运行测试

```bash
uv run poe test           # 或 python -m pytest -v
```

### 6. 停止服务

```bash
uv run poe infra-down     # docker compose down
```

## Platform Notes

### Windows
- Install Python 3.12+ from python.org or via `winget install Python.Python.3.12`
- Install uv: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Docker Desktop requires WSL2 — follow the Docker Desktop installer prompts

### macOS
- Install Python 3.12+: `brew install python@3.12`
- Install uv: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Docker Desktop, Colima, or OrbStack all work as Docker runtimes

## Commands

| Command   | Description                                | Usage                                      |
| --------- | ------------------------------------------ | ------------------------------------------ |
| diagnose  | Single-script crash diagnosis              | `mclaw diagnose --crash-log <path>`        |
| plan      | Dual-agent planning + execution            | `mclaw plan "<query>"`                     |
| solve     | Full Planner → Executor → Diagnoser flow   | `mclaw solve "<query>"`                    |
| monitor   | Watch crash reports dir for new files      | `mclaw monitor watch`                      |

## Project Structure

```
src/mclaw/
├── cli/          # CLI entry points for each stage
├── agents/       # LangGraph agents (Planner, Executor, Diagnoser)
├── mc_platform/  # Minecraft mod tools (query, crash parsing, compatibility)
├── llm/          # LLM provider abstraction
└── memory/       # ChromaDB memory system
```

## Stage 0 Accuracy

Crash diagnosis results using qwen3:4b via Ollama:

| Fixture | Expected | Diagnosed | Confidence | Correct |
|---------|----------|-----------|------------|---------|
| dependency_missing_jei.txt | dependency_missing | dependency_missing | 0.95 | ✓ |
| dependency_missing_kotlin.txt | dependency_missing | dependency_missing | 1.0 | ✓ |
| dependency_missing_create.txt | dependency_missing | version_conflict | 0.95 | ✗ |
| version_conflict_sodium.txt | version_conflict | version_conflict | 1.0 | ✓ |
| version_conflict_minecraft.txt | version_conflict | version_conflict | 1.0 | ✓ |
| version_conflict_optifine.txt | version_conflict | version_conflict | 0.95 | ✓ |
| ecosystem_fabric_on_forge.txt | ecosystem_incompatible | ecosystem_incompatible | 1.0 | ✓ |
| ecosystem_forge_on_fabric.txt | ecosystem_incompatible | ecosystem_incompatible | 1.0 | ✓ |

**Accuracy: 7/8 (87.5%)** — qwen3:4b correctly distinguishes all three categories. The single error is on a borderline case where an installed-but-outdated dependency could be classified either way.

## Development

```bash
uv run poe infra-up     # Start Docker services
uv run poe infra-down   # Stop Docker services
uv run poe test         # Run test suite
uv run poe test-watch   # Quick test run
```
