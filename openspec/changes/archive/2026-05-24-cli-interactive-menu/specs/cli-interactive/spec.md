## ADDED Requirements

### Requirement: Interactive menu on bare invocation

When `mclaw` is invoked without any subcommand, the system SHALL display an interactive menu allowing the user to select a function by number input.

#### Scenario: Menu displayed on bare invocation

- **WHEN** user runs `mclaw` without arguments
- **THEN** a numbered menu is displayed listing Diagnose, Plan, and Solve options

#### Scenario: Direct command invocation still works

- **WHEN** user runs `mclaw diagnose --crash-log <path>`
- **THEN** the diagnose command executes directly without showing the menu

### Requirement: Function selection and parameter input

The menu SHALL prompt the user to select a function by entering a number, then guide them through entering required parameters.

#### Scenario: Select Diagnose

- **WHEN** user enters `1` at the menu
- **THEN** the system prompts for a crash log file path, then executes diagnosis

#### Scenario: Select Plan

- **WHEN** user enters `2` at the menu
- **THEN** the system prompts for a natural language query, then executes the plan flow

#### Scenario: Select Solve

- **WHEN** user enters `3` at the menu
- **THEN** the system prompts for a natural language query, then executes the solve flow

#### Scenario: Invalid choice

- **WHEN** user enters an invalid number or text
- **THEN** the system displays an error message and re-shows the menu

### Requirement: Streaming step-by-step output

During execution, the system SHALL display progress messages as each step completes, rather than waiting until the end.

#### Scenario: Diagnose shows parsing then LLM progress

- **WHEN** user runs diagnose from the menu
- **THEN** the output shows "Parsing crash log..." followed by "Calling LLM for diagnosis..." and finally the result

#### Scenario: Plan shows task-by-task progress

- **WHEN** user runs plan from the menu
- **THEN** each planner-generated task is displayed with its status as it executes

#### Scenario: Solve shows all agent transitions

- **WHEN** user runs solve from the menu
- **THEN** the output shows Planner output, then Executor task progress, and Diagnoser result if triggered
