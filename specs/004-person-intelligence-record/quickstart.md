# Quickstart: NetworkOps V1 Person Intelligence Record

## Purpose

Use this quickstart to validate the V1 implementation once tasks are generated and code changes begin.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

## Scenario 1: Create Minimal Person

1. Create a person with only a name.
2. Reopen the app.
3. Confirm the person still exists.
4. Confirm optional fields display as unset or empty without error.

Expected result: Person creation requires only `name`.

## Scenario 2: Add Full Person Intelligence Record

1. Add identity fields such as alias, role, organization, location, and birthday.
2. Add relationship fields such as relationship type, status, strength, origin story, and importance reason.
3. Add dossier, interests, communication style, preferences, current goals, potential value, next action, and follow-up date.
4. Save and reopen.

Expected result: All values persist and remain editable.

## Scenario 3: Add Contact Methods

1. Add an email address.
2. Add a phone number.
3. Add LinkedIn, GitHub, and another social value.
4. Mark one contact method as primary where supported.
5. Save and reopen.

Expected result: Contact methods remain structured records attached to the correct person.

## Scenario 4: Add Multi-Person Interaction

1. Create at least two people.
2. Create one interaction involving both people.
3. Enter multiline summary, takeaways, and action items.
4. Save and reopen.

Expected result: The interaction links to both people and preserves multiline text.

## Scenario 5: Add Signal From Interaction

1. Create or open an interaction.
2. Add a signal for a person.
3. Reference the interaction as the source.
4. Add confidence where supported.

Expected result: Signal is a separate record linked to the person and optionally sourced from the interaction.

## Scenario 6: Add Multi-Person Opportunity

1. Create an opportunity such as mock interview, referral, collaboration, or portfolio review.
2. Link multiple people with roles.
3. Add status, description, and follow-up date.
4. Save and reopen.

Expected result: Opportunity remains separate from a generic task and keeps linked people.

## Scenario 7: Add Person-To-Person Relationship Link

1. Create two people.
2. Add a relationship link such as `mentors`, `works_with`, or `knows`.
3. Save and reopen both people.

Expected result: Relationship context is represented through `relationship_links`, not duplicated in person fields.

## Scenario 8: Profile Photo

1. Assign a local profile photo to a person.
2. Confirm the app stores a local asset reference.
3. Move or temporarily remove the photo file.
4. Reopen the person.

Expected result: Missing photo state is clear and does not block person access.

## Scenario 9: Long Multiline Text

1. Paste at least 2,000 characters into a long-form field.
2. Include line breaks, bullets, quotes, and URLs.
3. Save and reopen.

Expected result: Full content and line breaks are preserved.

## Scenario 10: Legacy Data Compatibility

1. Start with an existing database containing current people, contact-like fields, interactions, notes, open loops, suggestions, and evaluations.
2. Run the V1 migration after implementation exists.
3. Reopen existing people.

Expected result: Existing people remain accessible. Compatible contact, interaction, signal, relationship, and opportunity-like data is preserved. Standalone notes are not introduced as a new V1 entity.
