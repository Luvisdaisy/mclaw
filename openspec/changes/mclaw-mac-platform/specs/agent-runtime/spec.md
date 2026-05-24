## ADDED Requirements

### Requirement: LangGraph StateGraph orchestration

The Agent Runtime SHALL use LangGraph's StateGraph to orchestrate agent execution. The graph SHALL support conditional routing between Planner, Executor, and Diagnoser nodes based on execution state.

#### Scenario: Planner to Executor flow

- **WHEN** the Planner node completes and returns a valid task list
- **THEN** the state graph routes to the Executor node with the task list in state

#### Scenario: Executor to Diagnoser on failure

- **WHEN** the Executor node encounters a crash or error
- **THEN** the state graph routes to the Diagnoser node with the error context

#### Scenario: Diagnoser to Executor on fix suggestion

- **WHEN** the Diagnoser node produces a fix suggestion
- **THEN** the state graph routes back to the Executor to apply the fix

### Requirement: Planner Agent

The Planner Agent SHALL parse natural language user input and generate a structured, ordered task list. Each task SHALL include a description, expected tool to use, and expected output.

#### Scenario: Parse mod installation request

- **WHEN** the user inputs "Install Create mod to 1.20.1 Forge"
- **THEN** the Planner outputs tasks including: check Minecraft version compatibility, verify Forge compatibility, check dependencies, determine install feasibility

#### Scenario: Unclear request

- **WHEN** the user input is ambiguous or missing required information
- **THEN** the Planner SHALL ask clarifying questions instead of guessing

### Requirement: Executor Agent

The Executor Agent SHALL iterate through the task list and invoke MC Platform tools for each task. It SHALL collect results and update the shared state.

#### Scenario: Execute mod compatibility check

- **WHEN** the Executor receives a task to check mod compatibility
- **THEN** it calls the MC Platform compatibility tool and stores the result in state

#### Scenario: Tool execution failure

- **WHEN** a tool call fails (network error, invalid response)
- **THEN** the Executor records the failure in state and the graph routes to error handling

### Requirement: Diagnoser Agent

The Diagnoser Agent SHALL accept a Minecraft crash log and output a structured diagnosis including root cause category, confidence score, and a list of suspicious mods.

#### Scenario: Diagnose dependency missing crash

- **WHEN** given a crash log indicating a missing dependency
- **THEN** the Diagnoser categorizes it as "dependency missing" with confidence >= 0.7 and lists the missing mod

#### Scenario: Diagnose version conflict

- **WHEN** given a crash log with version mismatch errors
- **THEN** the Diagnoser categorizes it as "version conflict" and identifies the conflicting mods

#### Scenario: Diagnose Forge-Fabric incompatibility

- **WHEN** given a crash log with class loading errors from wrong mod loader
- **THEN** the Diagnoser categorizes it as "ecosystem incompatible (Forge vs Fabric)"

### Requirement: Stage-gated execution

The Agent Runtime SHALL support running at different stages (0-4). Each stage SHALL enable a specific subset of the agent graph. Stage 0 SHALL bypass LangGraph entirely and use a single LLM call.

#### Scenario: Stage 0 execution

- **WHEN** running with `--stage 0`
- **THEN** the system executes a single-script diagnosis flow without LangGraph orchestration

#### Scenario: Stage 1 execution

- **WHEN** running with `--stage 1`
- **THEN** only Planner and Executor nodes are active in the state graph
