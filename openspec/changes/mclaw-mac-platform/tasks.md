## 1. Project Scaffold and Dev Platform

- [ ] 1.1 Initialize Python project with `uv init`, create `pyproject.toml` with dependencies (langgraph, langchain, chromadb, pandas, tenacity, click, pytest)
- [ ] 1.2 Create `src/mclaw/` layout with subpackages: `cli/`, `agents/`, `mc_platform/`, `memory/`, `llm/`
- [ ] 1.3 Write `docker-compose.yml` with ChromaDB service and SQLite volume mount, test on Windows and macOS with Docker Desktop
- [ ] 1.4 Create `docker/` directory with ChromaDB configuration and README with cross-platform Docker setup instructions
- [ ] 1.5 Add `poethepoet` task runner in `pyproject.toml` for common operations: `poe infra-up`, `poe infra-down`, `poe test`
- [ ] 1.6 Write project `README.md` with setup instructions for Windows and macOS (uv, Docker Desktop)

## 2. CLI Entry Point

- [ ] 2.1 Implement `src/mclaw/cli/main.py` with click/typer entry point and `--stage` flag
- [ ] 2.2 Wire up subcommand groups: `mclaw stage0`, `mclaw stage1`, `mclaw stage2`
- [ ] 2.3 Add `--help` output showing all available commands and options

## 3. LLM Provider Layer

- [ ] 3.1 Implement `src/mclaw/llm/provider.py` with provider abstraction (OpenAI-compatible, Ollama)
- [ ] 3.2 Implement `src/mclaw/llm/retry.py` with tenacity exponential backoff and asyncio timeout
- [ ] 3.3 Add environment variable configuration: `MCLAW_LLM_PROVIDER`, `MCLAW_LLM_API_KEY`, `MCLAW_LLM_BASE_URL`, `MCLAW_LLM_MODEL`
- [ ] 3.4 Write tests for retry behavior and timeout handling

## 4. MC Platform Tools

- [ ] 4.1 Implement `src/mclaw/mc_platform/crash_parser.py` — parse Forge and Fabric crash logs into structured data
- [ ] 4.2 Implement `src/mclaw/mc_platform/mod_query.py` — query mod info from Modrinth API (primary) and CurseForge API (fallback) by name/ID/slug
- [ ] 4.3 Implement `src/mclaw/mc_platform/compatibility.py` — check mod compatibility with target Minecraft version and mod loader
- [ ] 4.4 Implement `src/mclaw/mc_platform/mod_cache.py` — SQLite-based mod metadata cache with TTL invalidation (24h default) and `--refresh` flag
- [ ] 4.5 Write tests with sample crash logs and mod data fixtures

## 5. Stage 0 — Prototype Validation

- [ ] 5.1 Implement `src/mclaw/cli/stage0.py` — single-script diagnosis via `mclaw stage0 diagnose --crash-log <path>` with one LLM call
- [ ] 5.2 Build prompt template for crash diagnosis covering the three target categories
- [ ] 5.3 Curate 5-10 real Minecraft crash logs as test fixtures
- [ ] 5.4 Run diagnosis on each fixture and record accuracy in README table
- [ ] 5.5 Verify Stage 0 correctly distinguishes "dependency missing", "version conflict", and "ecosystem incompatible" cases

## 6. Agent Runtime — LangGraph Integration

- [ ] 6.1 Define shared state schema (`AgentState`) for the LangGraph state graph
- [ ] 6.2 Implement `src/mclaw/agents/planner.py` — parse user input, output structured task list
- [ ] 6.3 Implement `src/mclaw/agents/executor.py` — iterate tasks, call MC Platform tools, update state
- [ ] 6.4 Build `src/mclaw/agents/graph.py` — StateGraph with Planner → Executor nodes and conditional routing
- [ ] 6.5 Implement `src/mclaw/cli/stage1.py` — wire Stage 1 CLI to the dual-agent graph

## 7. Stage 2 — Diagnoser Integration

- [ ] 7.1 Implement `src/mclaw/agents/diagnoser.py` — crash log in, root cause category + confidence + suspicious mods out
- [ ] 7.2 Add Diagnoser node to StateGraph with conditional routing from Executor on failure
- [ ] 7.3 Implement `src/mclaw/cli/stage2.py` — full Planner → Executor → Diagnoser flow
- [ ] 7.4 Verify Diagnoser reproduces Stage 0 test case results with equivalent accuracy

## 8. Memory System — ChromaDB

- [ ] 8.1 Implement `src/mclaw/memory/store.py` — connect to ChromaDB, create crash_cases collection
- [ ] 8.2 Implement `src/mclaw/memory/retriever.py` — semantic search over stored cases
- [ ] 8.3 Implement `src/mclaw/memory/embedder.py` — embed crash logs for storage and query
- [ ] 8.4 Integrate memory retrieval into Diagnoser flow (Stage 3): check cache before LLM call
- [ ] 8.5 Verify cache hit reduces diagnosis time by 50%+ for repeated crash scenarios
- [ ] 8.6 (Optional Stage 3+) Implement `src/mclaw/cli/monitor.py` — watchdog-based crash report directory watcher for automatic diagnosis on new crash files

## 9. Polish and Verification

- [ ] 9.1 Run full test suite on Windows and macOS and verify all tests pass
- [ ] 9.2 Verify end-to-end flow: `mclaw --stage 2 plan "Install Create to 1.20.1 Forge"` produces analysis output
- [ ] 9.3 Review all error messages for clarity and platform-specific guidance
- [ ] 9.4 Verify `uv sync && uv run pytest` succeeds on a clean checkout (both Windows and macOS)
