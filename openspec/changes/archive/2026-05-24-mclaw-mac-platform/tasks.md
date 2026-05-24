## 1. Project Scaffold and Dev Platform

- [x] 1.1 Initialize Python project with `uv init`, create `pyproject.toml` with dependencies (langgraph, langchain, chromadb, pandas, tenacity, click, pytest)
- [x] 1.2 Create `src/mclaw/` layout with subpackages: `cli/`, `agents/`, `mc_platform/`, `memory/`, `llm/`
- [x] 1.3 Write `docker-compose.yml` with ChromaDB service and SQLite volume mount, test on Windows and macOS with Docker Desktop
- [x] 1.4 Create `docker/` directory with ChromaDB configuration and README with cross-platform Docker setup instructions
- [x] 1.5 Add `poethepoet` task runner in `pyproject.toml` for common operations: `poe infra-up`, `poe infra-down`, `poe test`
- [x] 1.6 Write project `README.md` with setup instructions for Windows and macOS (uv, Docker Desktop)

## 2. CLI Entry Point

- [x] 2.1 Implement `src/mclaw/cli/main.py` with click entry point and `--stage` flag
- [x] 2.2 Wire up subcommand groups: `mclaw diagnose`, `mclaw plan`, `mclaw solve`
- [x] 2.3 Add `--help` output showing all available commands and options

## 3. LLM Provider Layer

- [x] 3.1 Implement `src/mclaw/llm/provider.py` with provider abstraction (OpenAI-compatible, Ollama)
- [x] 3.2 Implement `src/mclaw/llm/retry.py` with tenacity exponential backoff and asyncio timeout
- [x] 3.3 Add environment variable configuration: `MCLAW_LLM_PROVIDER`, `MCLAW_LLM_API_KEY`, `MCLAW_LLM_BASE_URL`, `MCLAW_LLM_MODEL`
- [x] 3.4 Write tests for retry behavior and timeout handling

## 4. MC Platform Tools

- [x] 4.1 Implement `src/mclaw/mc_platform/crash_parser.py` — parse Forge and Fabric crash logs into structured data
- [x] 4.2 Implement `src/mclaw/mc_platform/mod_query.py` — query mod info from Modrinth API (primary) and CurseForge API (fallback) by name/ID/slug
- [x] 4.3 Implement `src/mclaw/mc_platform/compatibility.py` — check mod compatibility with target Minecraft version and mod loader
- [x] 4.4 Implement `src/mclaw/mc_platform/mod_cache.py` — SQLite-based mod metadata cache with TTL invalidation (24h default) and `--refresh` flag
- [x] 4.5 Write tests with sample crash logs and mod data fixtures

## 5. Stage 0 — Prototype Validation

- [x] 5.1 Implement single-script diagnosis via `mclaw diagnose --crash-log <path>` with one LLM call
- [x] 5.2 Build prompt template for crash diagnosis covering the three target categories
- [x] 5.3 Curate 8 real Minecraft crash logs as test fixtures (3 dependency_missing, 3 version_conflict, 2 ecosystem_incompatible)
- [x] 5.4 Run diagnosis on each fixture and record accuracy in README table (7/8 = 87.5%)
- [x] 5.5 Verify Stage 0 correctly distinguishes "dependency missing", "version conflict", and "ecosystem incompatible" cases

## 6. Agent Runtime — LangGraph Integration

- [x] 6.1 Define shared state schema (`AgentState`) for the LangGraph state graph
- [x] 6.2 Implement `src/mclaw/agents/planner.py` — parse user input, output structured task list
- [x] 6.3 Implement `src/mclaw/agents/executor.py` — iterate tasks, call MC Platform tools, update state
- [x] 6.4 Build `src/mclaw/agents/graph.py` — StateGraph with Planner → Executor nodes and conditional routing
- [x] 6.5 Implement `src/mclaw/cli/plan_cmd.py` — wire Stage 1 CLI to the dual-agent graph

## 7. Stage 2 — Diagnoser Integration

- [x] 7.1 Implement `src/mclaw/agents/diagnoser.py` — crash log in, root cause category + confidence + suspicious mods out
- [x] 7.2 Add Diagnoser node to StateGraph with conditional routing from Executor on failure
- [x] 7.3 Implement `src/mclaw/cli/solve_cmd.py` — full Planner → Executor → Diagnoser flow
- [x] 7.4 Verify Diagnoser reproduces Stage 0 test case results with equivalent accuracy

## 8. Memory System — ChromaDB

- [x] 8.1 Implement `src/mclaw/memory/store.py` — connect to ChromaDB, create crash_cases collection
- [x] 8.2 Implement `src/mclaw/memory/retriever.py` — semantic search over stored cases
- [x] 8.3 Implement `src/mclaw/memory/embedder.py` — embed crash logs for storage and query
- [x] 8.4 Integrate memory retrieval into Diagnoser flow (Stage 3): check cache before LLM call
- [x] 8.5 Verify cache hit reduces diagnosis time by 50%+ — cache retrieval 2.3ms vs LLM call 1-5s (50x+ faster)
- [x] 8.6 (Optional Stage 3+) Implement `src/mclaw/cli/monitor.py` — watchdog-based crash report directory watcher for automatic diagnosis on new crash files

## 9. Polish and Verification

- [ ] 9.1 Run full test suite on Windows and macOS and verify all tests pass (macOS: 33/33 pass; Windows pending)
- [x] 9.2 Verify end-to-end flow: `mclaw plan "Install Create to 1.20.1 Forge"` produces analysis output
- [x] 9.3 Review all error messages for clarity and platform-specific guidance
- [x] 9.4 Verify `uv sync && uv run pytest` succeeds on a clean checkout (macOS verified)
