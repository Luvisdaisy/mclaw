## Context

mclaw is an Agent technology learning project. It uses Minecraft modpack building as a concrete practice domain — a problem space with real complexity (dependency resolution, version conflicts, crash diagnosis) that exercises core Agent skills. The project targets cross-platform support (Windows and macOS), with Windows as the initial development priority due to Minecraft's native ecosystem advantage. Docker Compose manages infrastructure services (SQLite + ChromaDB) on both platforms.

The project follows four stages (0-4), from single-script prototype through multi-agent orchestration with memory and evaluation. The tech stack is LangGraph + LangChain for agent orchestration, ChromaDB for semantic memory, SQLite for structured data, and Python with uv for dependency management.

## Goals / Non-Goals

**Goals:**
- Establish a clean Python project scaffold that works cross-platform (Windows + macOS) out of the box
- Provide Docker Compose infra (SQLite + ChromaDB) running on Docker Desktop for both Windows and macOS
- Build a CLI that serves as the primary interaction surface for all stages
- Implement LangGraph-based agent orchestration with Planner, Executor, and Diagnoser
- Deliver MC platform tools: mod info query (Modrinth primary, CurseForge secondary), compatibility analysis, crash log parsing
- Implement SQLite-based mod metadata cache with TTL-based invalidation for API data freshness
- Provide ChromaDB memory layer for storing and retrieving historical crash cases
- Validate Stage 0 with real Minecraft crash logs on Windows before committing to Stage 1+

**Non-Goals:**
- Electron UI or graphical interface (CLI only for now)
- Repairer, Evaluator, or other extended Agent roles (Stage 4+ stretch goals)
- Production deployment, scaling, or multi-user support
- Linux support (Windows + macOS only; Linux is nice-to-have but not actively validated)
- Agent voting/negotiation or reflection memory (post-Stage 4 explorations)

## Decisions

### 1. uv as package manager over pip/poetry

uv is significantly faster than pip/poetry, handles virtual environments automatically, and has first-class Windows + macOS support. It keeps the dev setup to two commands (`uv sync && uv run pytest`) on both platforms, critical for a learning project where low friction matters.

### 2. LangGraph StateGraph over custom state machine or CrewAI

LangGraph provides built-in checkpointing, conditional edges, and a well-documented state graph model. It aligns with the learning goal (understanding Agent orchestration). CrewAI is higher-level but obscures the state management internals we want to learn. A custom state machine would violate "don't reinvent the wheel."

### 3. ChromaDB in Docker rather than embedded mode

While ChromaDB can run embedded, Docker isolation matches the project's intent to learn real infrastructure patterns. Docker Compose also manages SQLite via a simple volume mount, giving a unified infra start/stop experience. Docker Desktop is the standard runtime on both Windows and macOS — one install, identical commands across platforms.

### 4. Separate MC Platform layer from Agent Runtime

The MC tools (mod query, crash parsing) are pure functions with no Agent dependency. Keeping them in a separate `mc_platform` package allows them to be tested independently and potentially reused outside the Agent context.

### 5. CLI-first interaction model

Each stage is exposed as a CLI subcommand (`mclaw stage0 diagnose`, `mclaw stage1 plan`, etc.). This keeps the interface consistent across stages and avoids the complexity of a REPL or web UI during learning phases.

### 6. Stage-gated implementation with feature flags

Stages 0-4 are enabled via a `--stage` flag or config. This prevents later-stage code from complicating earlier-stage execution and makes it easy to demo progress at each stage boundary.

### 7. LLM provider abstraction with LiteLLM-compatible interface

Rather than hardcoding a single LLM provider, the system uses a thin provider abstraction that supports OpenAI-compatible APIs. This lets the learner switch between local (Ollama, LM Studio) and cloud providers without code changes. tenacity handles retry/backoff; asyncio handles timeouts.

### 8. poethepoet as cross-platform task runner over Makefile

Makefile requires MSYS2/GnuWin on Windows, adding an unnecessary setup step. poethepoet is a pure-Python task runner that lives in `pyproject.toml`, works identically on Windows and macOS, and integrates naturally with the uv ecosystem (`uv run poe infra-up`). No extra install beyond `uv sync`.

### 9. Modrinth as primary mod data source, CurseForge as secondary

Modrinth's API is fully public (no API key required), has excellent OpenAPI documentation, and exposes faceted search with precise version/loader compatibility filtering. It covers the vast majority of actively maintained mods. CurseForge is added as a fallback for legacy mods only available there, but requires an API key and has stricter rate limits. The query flow: try Modrinth first → if not found, try CurseForge → cache the result.

### 10. SQLite-based mod metadata cache with TTL invalidation

Repeatedly querying mod APIs for the same data wastes resources and adds latency. A local SQLite cache stores mod metadata keyed by (source, mod_id) with a `last_updated` timestamp. Default TTL is 24 hours. On query: check cache → if fresh, return cached; if stale, re-fetch from API and update cache. A `--refresh` flag forces bypass. This uses the same SQLite infrastructure already planned, avoiding new dependencies.

### 11. Manual CLI crash log input for Stage 0-2, file watcher optional for Stage 3+

For early stages, the simplest integration is a CLI argument: `mclaw stage0 diagnose --crash-log <path>`. The user provides the crash report path directly. For Stage 3+ (memory system), an optional `mclaw monitor` subcommand can watch `%APPDATA%\.minecraft\crash-reports\` (Windows) or `~/Library/Application Support/minecraft/crash-reports/` (macOS) for new files using watchdog, enabling automatic diagnosis and cache lookup. Process-level monitoring (detecting MC exit code) is deferred as a post-Stage 4 exploration.

## Risks / Trade-offs

- **Docker dependency as setup hurdle**: Docker Desktop requires installation on both platforms → Mitigation: Document setup clearly, consider optional SQLite-only fallback for Stage 0-1 so basic functionality works without Docker
- **Mod metadata cache staleness**: Cached mod data can become outdated, leading to incorrect compatibility analysis → Mitigation: TTL-based invalidation (24h default), `--refresh` flag for forced re-fetch, display cache age in CLI output so users can judge freshness
- **LangGraph version churn**: LangGraph API is evolving rapidly → Mitigation: Pin versions in pyproject.toml, test upgrades intentionally as a learning exercise
- **LLM cost during development**: Frequent LLM calls during iteration add up → Mitigation: Support local models via Ollama from Stage 0, cache LLM responses in dev mode
- **Scope creep**: Agent learning projects tend to expand into product-building → Mitigation: Strict stage gating, each stage has a clear Done definition from the project doc
