## ADDED Requirements

### Requirement: Project scaffold with uv

The project SHALL use uv as the package manager with a `pyproject.toml` at the repo root. Running `uv sync` SHALL install all dependencies and create a virtual environment. The source layout SHALL follow `src/mclaw/` convention.

#### Scenario: Clean checkout and install

- **WHEN** a developer clones the repo and runs `uv sync` on Windows or macOS
- **THEN** all dependencies install without errors and `uv run pytest` executes successfully

#### Scenario: Project structure

- **WHEN** inspecting the project layout
- **THEN** the following directories exist: `src/mclaw/`, `src/mclaw/cli/`, `src/mclaw/agents/`, `src/mclaw/mc_platform/`, `src/mclaw/memory/`, `tests/`, `docker/`

### Requirement: Docker Compose infrastructure

The project SHALL provide a `docker-compose.yml` that starts SQLite (via a volume-mounted file) and ChromaDB services. Docker Compose SHALL work with Docker Desktop on both Windows and macOS.

#### Scenario: Start infrastructure

- **WHEN** running `docker compose up -d` from the project root
- **THEN** ChromaDB is accessible at `localhost:8000` and SQLite data directory is mounted at `./data/`

#### Scenario: Cross-platform Docker runtime compatibility

- **WHEN** running `docker compose up` on Windows (Docker Desktop) or macOS (Docker Desktop)
- **THEN** all services start without platform-specific errors

### Requirement: CLI entry point

The project SHALL provide a `mclaw` CLI command with stage-based subcommands. The CLI SHALL be built with `click` or `typer`.

#### Scenario: Help output

- **WHEN** running `mclaw --help`
- **THEN** available subcommands for each stage are listed with descriptions

#### Scenario: Stage selection

- **WHEN** running `mclaw --stage 0 diagnose --log crash.txt`
- **THEN** the Stage 0 diagnosis flow executes with the specified crash log

### Requirement: Cross-platform task runner

The project SHALL use poethepoet as a cross-platform task runner, configured in `pyproject.toml`. Common operations (`infra-up`, `infra-down`, `test`) SHALL be executable via `uv run poe <task>` on both Windows and macOS.

#### Scenario: Run infrastructure tasks

- **WHEN** running `uv run poe infra-up` on Windows or macOS
- **THEN** Docker Compose starts all services

#### Scenario: Run test suite

- **WHEN** running `uv run poe test`
- **THEN** pytest executes the full test suite on either platform

### Requirement: LLM provider abstraction

The system SHALL provide an LLM provider layer that supports OpenAI-compatible APIs and local models (Ollama). It SHALL use tenacity for retry with exponential backoff and asyncio for call timeouts.

#### Scenario: Retry on transient failure

- **WHEN** an LLM API call fails with a 429 or 5xx status
- **THEN** the call is retried up to 3 times with exponential backoff

#### Scenario: Timeout handling

- **WHEN** an LLM API call exceeds the configured timeout (default 60s)
- **THEN** the call is cancelled and a timeout error is raised

#### Scenario: Provider switching

- **WHEN** the `MCLAW_LLM_PROVIDER` environment variable is set to `ollama`
- **THEN** all LLM calls route to the local Ollama endpoint
