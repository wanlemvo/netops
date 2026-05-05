# TUI Screen Contract: NetOps

The TUI launches from `netops tui` and uses the same services and records as direct commands. Every save action must validate input, preserve entered values after errors, and show a confirmation when completed.

## Navigation

**Required main menu entries**:
- Overview
- People
- Dossier
- Timeline
- Suggestions
- Evaluation
- Quit

Users must be able to reach every required screen within three selections from the main menu.

## Overview Dashboard

**Purpose**: Show the current relationship workload at a glance.

**Required content**:
- Total people
- Recent interactions
- Open loops count
- Overdue follow-ups
- Due-soon follow-ups
- Top suggested actions
- Empty-state guidance for new workspaces

**Primary actions**:
- Add person
- Log interaction
- View suggestions
- Open people directory

## People Directory

**Purpose**: Browse and select tracked people.

**Required content**:
- Display name
- Organization or relationship context when available
- Tags when available
- Last interaction date
- Open-loop status

**Primary actions**:
- Add person
- Search/filter people
- Open dossier
- Log interaction for selected person

## Dossier View

**Purpose**: Consolidate relationship context for one person.

**Required content**:
- Person details
- Relationship notes
- Related people when available
- Open loops
- Recent interactions
- Suggestions for this person
- Outcome evaluations

**Primary actions**:
- Edit person details
- Add relationship note
- Log interaction
- Close or defer open loop
- Evaluate outcome

## Interaction Timeline

**Purpose**: Review historical interactions chronologically.

**Required content**:
- Interaction date
- Interaction type
- Notes summary
- Related follow-up or open loop
- Evaluation indicator when present

**Primary actions**:
- Filter by person
- Add interaction
- Open related dossier
- Create or close open loop

## Suggestions Screen

**Purpose**: Help the user choose next actions.

**Required content**:
- Suggested action text
- Target person
- Priority indicator
- Explanation reason
- Related open loop or history

**Primary actions**:
- Accept suggestion
- Ignore suggestion
- Mark completed
- Evaluate completed action
- Open related dossier

## Evaluation Screen

**Purpose**: Record and review action outcomes.

**Required content**:
- Candidate completed actions or interactions
- Outcome choice
- Notes input
- Prior evaluations for context

**Primary actions**:
- Save evaluation
- Edit notes before save
- Return to dossier or suggestions

## TUI Error Contract

Screens must handle:
- Empty data states
- Ambiguous person selection
- Invalid dates
- Missing required fields
- Storage read/write failures
- Terminal too small for comfortable layout

Errors must keep the user in context and explain the next corrective action.
