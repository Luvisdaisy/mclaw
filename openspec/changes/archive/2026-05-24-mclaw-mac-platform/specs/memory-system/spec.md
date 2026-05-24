## ADDED Requirements

### Requirement: Store crash case

The system SHALL store diagnosed crash cases in ChromaDB. Each case SHALL include the crash log text, the diagnosis result, the root cause category, and an embedding of the crash log for semantic retrieval.

#### Scenario: Store successful diagnosis

- **WHEN** a crash is successfully diagnosed with category and confidence
- **THEN** the case is stored in ChromaDB with metadata including category, timestamp, and confidence score

#### Scenario: Store failed diagnosis

- **WHEN** a crash diagnosis produces low confidence (< 0.5)
- **THEN** the case is stored with a "low_confidence" flag for later review

### Requirement: Retrieve similar cases

The system SHALL support semantic search over stored crash cases. Given a new crash log, it SHALL return the top-K most similar historical cases with their diagnoses.

#### Scenario: Find similar crash

- **WHEN** querying with a crash log about a missing dependency
- **THEN** the top result is a previously stored case with the same "dependency missing" category

#### Scenario: No similar cases

- **WHEN** querying with a crash log that has no semantic match in the database
- **THEN** an empty result list is returned with distance scores above the configured threshold

### Requirement: Diagnosis acceleration through memory

When the Memory System is active (Stage 3+), the Diagnoser SHALL check historical cases before performing a full LLM diagnosis. If a sufficiently similar case exists (similarity score > threshold), it SHALL return the cached diagnosis.

#### Scenario: Cache hit

- **WHEN** a crash log is similar to a previously diagnosed case (similarity > 0.9)
- **THEN** the cached diagnosis is returned without an LLM call, reducing response time

#### Scenario: Cache miss

- **WHEN** a crash log has no similar case above threshold
- **THEN** a full LLM diagnosis is performed and the result is stored as a new case

### Requirement: Optional crash report directory watcher (Stage 3+)

The system MAY provide a `mclaw monitor` subcommand that watches the Minecraft crash reports directory for new files and triggers automatic diagnosis. On Windows, the default watch path SHALL be `%APPDATA%\.minecraft\crash-reports\`. On macOS, the default SHALL be `~/Library/Application Support/minecraft/crash-reports/`.

#### Scenario: New crash file detected

- **WHEN** a new crash report file appears in the watched directory
- **THEN** the system automatically parses the crash log, performs diagnosis (checking memory cache first), and outputs the result

#### Scenario: Monitor on non-existent directory

- **WHEN** the monitor is started but the crash reports directory does not exist
- **THEN** the monitor warns the user and waits, retrying the directory check periodically
