# Contract: NetworkOps V1 CLI/TUI Behavior

## Scope

This contract defines user-facing behavior expected from CLI and terminal UI surfaces after the V1 schema implementation.

## Person Profile Behavior

- The app must let a user create a person with only a name.
- The app must let a user view and edit V1 person fields.
- The app must not expose `mutual_connections` as an editable field.
- Person-to-person context must be represented through relationship links.

## Contact Behavior

- The app must expose dedicated contact method flows for email, phone, LinkedIn, GitHub, and other social values.
- Contact methods must remain attached to the correct person after restart.
- The app should clearly show primary contact methods when available.

## Interaction Behavior

- The app must allow an interaction to include multiple people.
- The app must preserve multiline summaries, takeaways, and action items.
- The app must make linked people visible when viewing an interaction.

## Signal Behavior

- The app must allow a user to capture relationship signals about a person.
- The app must support optional confidence and optional interaction source context.
- Signals must not be flattened into the person dossier text.

## Opportunity Behavior

- The app must allow opportunities to involve multiple people.
- The app must expose status and follow-up date.
- Opportunities must remain separate from generic tasks and open-loop mechanics unless a later migration plan maps compatible legacy data.

## Profile Photo Behavior

- The app must store/import profile photos as local assets.
- The app must store only a path/reference in the database.
- Missing or unsupported photo files must not prevent opening or editing a person.

## Long-Form Text Behavior

- Long-form fields must support pasted text beyond the visible terminal window.
- Multiline input must preserve line breaks after save/reload.
- Viewing and editing must not operate only on the visible slice of text.

## Out Of Scope

- Standalone note-taking workflows
- AI-generated summaries or suggestions
- Semantic search
- Graph visualization
- External integrations
