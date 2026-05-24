## Why

mclaw is an Agent technology learning project that uses Minecraft modpack building as its practice domain. It needs a cross-platform development platform (Python project scaffold, Docker Compose infra, CLI tooling) and an MC platform (Minecraft mod query via Modrinth/CurseForge, compatibility analysis, crash diagnosis tools) — designed to run on Windows and macOS, with Windows as the initial development priority.

## What Changes

- **New**: Python project scaffold with uv package manager, pytest, and project structure
- **New**: Docker Compose infrastructure for SQLite + ChromaDB, configured for macOS (Colima/OrbStack compatibility)
- **New**: CLI entry point (`mclaw`) for running agent workflows from the terminal
- **New**: LLM provider abstraction layer with tenacity-based retry and asyncio timeout
- **New**: LangGraph-based Agent Runtime with Planner → Executor → Diagnoser state graph
- **New**: MC Platform tool layer — mod info querying (Modrinth API primary, CurseForge API secondary), compatibility analysis, crash log parsing
- **New**: SQLite-based mod metadata cache with TTL invalidation for API data freshness
- **New**: Memory system with ChromaDB for storing and retrieving crash cases
- **New**: Stage 0 prototype — single-script crash diagnosis validation

## Capabilities

### New Capabilities

- `dev-platform`: Python project scaffold, Docker Compose infra, CLI tooling, poethepoet task runner, and LLM provider layer — validated on Windows and macOS
- `agent-runtime`: LangGraph-based StateGraph orchestrating Planner, Executor, and Diagnoser agents with state management
- `mc-platform`: Minecraft mod query tools, compatibility analysis, crash log parsing and diagnosis
- `memory-system`: ChromaDB-backed semantic memory for storing and retrieving historical crash cases

### Modified Capabilities

<!-- No existing capabilities to modify -->

## Impact

- New Python project at repo root with `pyproject.toml` (including poethepoet tasks), `src/mclaw/` layout
- Docker Compose configuration in `docker/` directory
- New CLI via `click` or `typer` at `src/mclaw/cli/`
- LangGraph, LangChain, ChromaDB, pandas, tenacity, poethepoet as core dependencies
- Windows and macOS setup notes in README — Docker Desktop as the unified Docker runtime on both platforms
