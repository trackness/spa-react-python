# Standards

The standards every change in this repository follows.

## Dependencies

Reach for a strong existing implementation before writing code of your own: anything a well-maintained library already does is used, never hand-rolled. A good dependency is preferred to bespoke code.

## Toolchain

- **ty** type checks Python.
- **ruff** lints and formats Python.
- **Biome** lints and formats the Frontend.

## Python

- `from __future__ import annotations` is banned.
- **Pydantic v2** is the preferred tool for data models and validation, and **pydantic-settings** for Settings.

## API errors and forms

- Every API error reaches the Frontend as a thrown, typed error carrying the HTTP status and the response body.
- Every form shows the Backend's validation errors against the fields they belong to.

## Taskfile

- Every change that introduces a local action delivers its Taskfile task in the same change.
- CI and prek call tasks, never the underlying commands.

## Telemetry off

- Nothing used may report usage or errors about the repository's owner. Version lookups and downloads are acceptable.
- Every tool a change introduces is checked for usage or error reporting, and that reporting is switched off in the same change.
