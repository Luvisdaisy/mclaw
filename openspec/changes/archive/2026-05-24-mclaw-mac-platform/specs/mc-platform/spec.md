## ADDED Requirements

### Requirement: Mod information query

The system SHALL provide a tool to query Minecraft mod information by name, ID, or slug. It SHALL query the Modrinth API as the primary data source, falling back to the CurseForge API when a mod is not found on Modrinth. Results SHALL include mod name, version, supported Minecraft versions, mod loader (Forge/Fabric/NeoForge/Quilt), and dependencies.

#### Scenario: Query existing mod

- **WHEN** querying for "Create" mod
- **THEN** the result includes the mod's supported Minecraft versions, mod loader, and dependency list

#### Scenario: Query non-existent mod

- **WHEN** querying for a mod name that doesn't exist
- **THEN** the tool returns an empty result with a "not found" status

### Requirement: Compatibility analysis

The system SHALL analyze whether a set of mods are compatible with a target Minecraft version and mod loader. The analysis SHALL check version constraints and mod loader requirements.

#### Scenario: Compatible mod set

- **WHEN** analyzing "Create v0.5.1" for "Minecraft 1.20.1 Forge"
- **THEN** the result indicates compatibility and lists any required dependencies

#### Scenario: Incompatible mod loader

- **WHEN** analyzing a Fabric-only mod for a Forge target
- **THEN** the result indicates incompatibility with reason "mod loader mismatch"

#### Scenario: Version mismatch

- **WHEN** analyzing a mod built for Minecraft 1.19.2 against a 1.20.1 target
- **THEN** the result indicates incompatibility with reason "Minecraft version mismatch"

### Requirement: Mod metadata cache

The system SHALL cache mod metadata locally in SQLite to reduce redundant API calls. Each cache entry SHALL be keyed by (source, mod_id) and include the full mod metadata JSON and a `last_updated` timestamp. The default TTL SHALL be 24 hours, with a `--refresh` flag to force bypass.

#### Scenario: Cache hit

- **WHEN** querying for a mod that was fetched within the TTL window
- **THEN** the cached data is returned without an API call

#### Scenario: Cache miss (stale)

- **WHEN** querying for a mod whose cache entry is older than the TTL
- **THEN** the API is re-queried, the cache is updated, and fresh data is returned

#### Scenario: Force refresh

- **WHEN** querying with the `--refresh` flag
- **THEN** the cache is bypassed, the API is queried directly, and the cache is updated

### Requirement: Crash log parsing

The system SHALL parse Minecraft crash logs and extract structured information: crash type, stack trace, referenced mods, and error messages. It SHALL handle both Forge and Fabric crash log formats.

#### Scenario: Parse Forge crash log

- **WHEN** given a Forge crash log with a `java.lang.NoClassDefFoundError`
- **THEN** the parser extracts the missing class name, the mod that referenced it, and the full stack trace

#### Scenario: Parse Fabric crash log

- **WHEN** given a Fabric crash log with a `java.lang.RuntimeException`
- **THEN** the parser extracts the error message, involved mods, and crash context

#### Scenario: Malformed crash log

- **WHEN** given a file that is not a valid Minecraft crash log
- **THEN** the parser returns an error indicating "unrecognized format" rather than crashing

### Requirement: Crash diagnosis (Stage 0 prototype)

The system SHALL provide a Stage 0 prototype that takes a crash log path via `--crash-log <path>` and uses a single LLM call to diagnose the root cause. The output SHALL classify the crash into one of three categories: "dependency missing", "version conflict", or "ecosystem incompatible (Forge vs Fabric)".

#### Scenario: Diagnose dependency missing

- **WHEN** given a crash log caused by a missing mod dependency
- **THEN** the LLM diagnoses it as "dependency missing" with the specific missing mod name

#### Scenario: Diagnose version conflict

- **WHEN** given a crash log caused by incompatible mod versions
- **THEN** the LLM diagnoses it as "version conflict" with the conflicting mod names

#### Scenario: Diagnose ecosystem incompatibility

- **WHEN** given a crash log caused by loading a Fabric mod on Forge
- **THEN** the LLM diagnoses it as "ecosystem incompatible (Forge vs Fabric)"
