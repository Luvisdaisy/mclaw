## MODIFIED Requirements

### Requirement: Interactive menu on bare invocation

When `mclaw` is invoked without any subcommand, the system SHALL display an interactive menu allowing the user to select a function using arrow keys. The menu SHALL be implemented using prompt_toolkit for keyboard navigation and SHALL use Rich-compatible styling.

#### Scenario: Menu displayed on bare invocation

- **WHEN** user runs `mclaw` without arguments
- **THEN** an interactive menu is displayed with Rich-formatted panel, listing Diagnose, Plan, and Solve options with arrow-key navigation

#### Scenario: Direct command invocation still works

- **WHEN** user runs `mclaw diagnose --crash-log <path>`
- **THEN** the diagnose command executes directly without showing the menu

### Requirement: Arrow key navigation

The menu SHALL support moving the selection cursor with ↑ and ↓ arrow keys. The currently selected option SHALL be visually highlighted.

#### Scenario: Arrow down moves selection

- **WHEN** user presses ↓ at the menu
- **THEN** the selection highlight moves to the next option

#### Scenario: Arrow up moves selection

- **WHEN** user presses ↑ at the menu
- **THEN** the selection highlight moves to the previous option

#### Scenario: Enter confirms selection

- **WHEN** user presses Enter while an option is highlighted
- **THEN** the highlighted option is selected and the menu exits

## ADDED Requirements

### Requirement: prompt_toolkit dependency

The project SHALL include `prompt_toolkit` as a direct dependency for keyboard input handling.

#### Scenario: Dependency installed

- **WHEN** running `uv sync`
- **THEN** prompt_toolkit is available for import
