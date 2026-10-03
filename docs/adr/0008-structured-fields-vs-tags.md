# ADR 0008: Structured Fields vs Tags

## Status

Proposed

## Problem

Excessive reliance on tags causes tag sprawl and inconsistent classification.

Examples:

- cybersecurity
- cyber security
- security
- infosec

These may represent the same concept, but if they are entered as unrelated tags, filtering and reporting become unreliable. The same problem appears with relationship types, statuses, confidence levels, opportunity states, and other values that need consistency.

## Decision

Use structured fields whenever values come from a controlled list. Use tags only for flexible classification and discovery.

Examples of structured fields:

`relationship_type`:

- mentor
- peer
- friend
- family
- recruiter

`relationship_status`:

- active
- dormant
- archived

Other likely controlled fields include relationship strength, opportunity status, signal confidence, sentiment, contact method type, and follow-up status.

Tags should remain available for flexible labels that do not require strict workflow meaning.

## Rationale

This follows Notion and CRM design practices and improves filtering, reporting, and consistency. Notion-style databases separate select fields from tags because select fields encode expected structure. CRM systems use controlled values for operational states because those values drive filtering, dashboards, workflows, and reporting.

NetworkOps should use the same pattern: structured fields for operational meaning, tags for flexible discovery.

## Consequences

- Filtering and reporting become more consistent.
- Relationship and opportunity states can drive future workflows more reliably.
- Tags remain useful without becoming the only classification tool.
- Some values need controlled vocabularies and validation.
- The app may need a path for adding or revising controlled values later.

## Non-Goals

- This decision does not remove tags.
- This decision does not require every field to use a controlled list.
- This decision does not implement recommendation systems or automatic classification.
- This decision does not create database migrations yet.
