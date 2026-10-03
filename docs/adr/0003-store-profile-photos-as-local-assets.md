# ADR 0003: Store Profile Photos as Local Assets

## Status

Proposed

## Context

NetworkOps V1 needs profile photos for person records. The app is local-first and should remain portable across machines when the app folder and data folder are moved together.

## Decision

Store profile photos as local files under the app data directory and store only the photo path or asset reference in the database.

## Consequences

- The database remains smaller and easier to inspect, back up, and migrate.
- Photos can move with the portable app folder when stored under `data/assets/profile_photos/`.
- Missing or unsupported photo files can be handled gracefully without corrupting person records.
- The app must manage asset import, filename collisions, missing files, and relative paths.

## Non-Goals

- This decision does not require storing images as database blobs.
- This decision does not define advanced image editing, remote image fetching, or cloud media storage.
