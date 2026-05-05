# CLI Command Contract: NetOps

All commands must support human-readable output. Commands that return structured data should also support `--json` where practical. Validation failures must exit non-zero and explain what to fix without discarding user-entered context in interactive prompts.

## Global Commands

### `netops --help`

Shows available command groups and common options.

### `netops tui`

Launches the interactive terminal interface at the overview dashboard.

## People

### `netops people add`

Creates a person.

**Inputs**:
- `--name TEXT` required unless prompted
- `--email TEXT` optional
- `--phone TEXT` optional
- `--organization TEXT` optional
- `--tag TEXT` repeatable
- `--notes TEXT` optional

**Success output**:
- Confirms the person was created
- Shows the new person identifier and display name

### `netops people list`

Lists people with identifying context.

**Options**:
- `--tag TEXT` optional filter
- `--search TEXT` optional name or note search
- `--json` optional structured output

## Relationships

### `netops relationship add PERSON`

Adds relationship context for a person.

**Inputs**:
- `PERSON`: person id or unambiguous display name
- `--type TEXT` required unless prompted
- `--related-person TEXT` optional
- `--notes TEXT` optional

## Interactions

### `netops log PERSON`

Logs an interaction for a person.

**Inputs**:
- `PERSON`: person id or unambiguous display name
- `--date DATE` optional, defaults to today
- `--type TEXT` required unless prompted
- `--notes TEXT` required unless prompted
- `--follow-up TEXT` optional open-loop description
- `--due DATE` optional follow-up due date

**Success output**:
- Confirms the interaction was saved
- Shows any created open loop

## Open Loops

### `netops loops list`

Lists open, overdue, deferred, or completed loops.

**Options**:
- `--person TEXT` optional filter
- `--status open|completed|deferred|closed_no_action` optional filter
- `--overdue` optional filter
- `--json` optional structured output

### `netops loops close LOOP_ID`

Closes or defers an open loop.

**Inputs**:
- `LOOP_ID`: required open-loop identifier
- `--status completed|deferred|closed_no_action` required unless prompted
- `--notes TEXT` optional resolution notes
- `--due DATE` optional new due date when deferring

## Suggestions

### `netops suggest`

Shows prioritized next actions.

**Options**:
- `--person TEXT` optional person filter
- `--limit INTEGER` optional maximum result count, default 10
- `--include-low-priority` optional flag
- `--json` optional structured output

**Success output**:
- Displays action text, person, priority, and reason
- Clearly communicates when no useful suggestions exist

## Evaluations

### `netops evaluate`

Records an outcome evaluation.

**Inputs**:
- `--person TEXT` required unless implied by action or interaction
- `--action ID` optional suggested action id
- `--interaction ID` optional interaction id
- `--outcome positive|neutral|negative|unknown` required unless prompted
- `--notes TEXT` optional
- `--date DATE` optional, defaults to today

**Success output**:
- Confirms the evaluation was saved
- Shows where it will appear in the dossier

## Error Contract

Commands must produce consistent error categories:
- Missing required input
- Unknown person or ambiguous person match
- Unknown record identifier
- Invalid date or future date requiring confirmation
- Storage unavailable or unreadable
- Validation failed

Each error must include a short corrective next step.
