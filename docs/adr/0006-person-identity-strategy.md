# ADR 0006: Person Identity Strategy

## Status

Proposed

## Problem

Names are not unique. A user may create records such as:

- Isaac
- Rei
- Dr. Olav
- Dr Olav

These records may refer to the same person, different people, aliases, incomplete names, or records entered at different times with different levels of confidence. Email addresses, phone numbers, and social accounts can also change, be missing, or be shared across contexts.

If NetworkOps treats a display name as the true identity of a person, it will either block legitimate records or merge records too aggressively. Real-world relationship data is imperfect, so identity resolution needs to preserve flexibility.

## Decision

Use UUIDs as the true identity for every person record.

Names, aliases, emails, phone numbers, social accounts, and organizations are attributes of a person record. They are not the true identifier.

NetworkOps V1 should implement duplicate detection rather than duplicate prevention. Potential duplicate records should generate warnings, but they should not block record creation.

Future duplicate detection should compare:

- Name similarity
- Email
- Phone
- LinkedIn
- GitHub
- Other social accounts

## Rationale

This follows common CRM identity-resolution patterns while preserving flexibility for imperfect real-world data. Salesforce, HubSpot, and similar systems generally treat contacts or leads as records with stable internal IDs, while names and contact methods are attributes that can be compared, changed, enriched, or merged later.

UUID-backed identity also supports future graph-style relationships because links can point to stable person IDs instead of fragile display names.

## Consequences

- Two people can have the same or similar names without corrupting data.
- A single person can have multiple contact methods, aliases, or naming variations.
- The system can warn about possible duplicates without blocking fast capture.
- Future merge and deduplication workflows can be built around stable IDs.
- Users may temporarily have duplicate-looking records until they choose to resolve them.

## Non-Goals

- This decision does not implement automatic merging.
- This decision does not implement AI identity resolution.
- This decision does not block users from creating duplicate-looking records.
- This decision does not create database migrations yet.
