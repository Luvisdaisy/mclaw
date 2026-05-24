# mclaw

Agent technology learning project using Minecraft modpack building as a practice domain.

## Prerequisites

- **Python 3.12+** — [Download](https://www.python.org/downloads/)
- **uv** — Python package manager, [install](https://docs.astral.sh/uv/getting-started/installation/)
- **Docker Desktop** — For ChromaDB service, [Download](https://www.docker.com/products/docker-desktop/)

## Quick Start

```bash
# Clone and install
git clone <repo-url> && cd mclaw
uv sync

# Start infrastructure
uv run poe infra-up

# Run tests
uv run poe test
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
