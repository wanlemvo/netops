# ADR 0004: Support Long-Form Multiline Text

## Status

Proposed

## Context

NetworkOps is valuable because it preserves relationship context. Fields such as dossier, origin story, importance reason, notes, summaries, takeaways, action items, signals, and opportunity descriptions may contain pasted paragraphs, bullets, and line breaks. The current app has shown issues when text does not fit within the visible window.

## Decision

Store long-form content as multiline text without artificial truncation, and design CLI entry/editing flows so visible terminal size does not limit the stored value.

## Consequences

- Long-form fields can preserve the context that makes NetworkOps useful.
- Pasted text and line breaks should survive save and reload.
- CLI interfaces must distinguish short single-line fields from multiline fields.
- Display and editing flows must wrap, scroll, page, or otherwise navigate content that is larger than the window.
- Tests should cover long pasted text, multiline text, and terminal-size edge cases.

## Non-Goals

- This decision does not implement rich text formatting.
- This decision does not require semantic parsing or AI summarization.
