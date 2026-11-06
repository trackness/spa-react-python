# Standards

The standards every change in this repository follows.

## Dependencies

Never hand-roll anything a strong implementation already does. Good dependencies are not to be avoided. Follow a framework's standard tooling and patterns unless there is a need to deviate.

Before writing anything, read the dependencies' source (`backend/.venv`, `*/node_modules`, and each GitHub Action's `action.yml` and source at the version it pins, fetched with `gh api`) for a built-in or standard hook that already does it. Never contort a dependency into a place it does not belong.

## Comments

A comment says only why the code is as it is now: no tombstones, and no decision history.

## Toolchain

- **ty** type checks Python.
- **ruff** lints and formats Python.
- **Biome** lints and formats the Frontend and the end-to-end tests.

## Python

- `from __future__ import annotations` is banned.
- **Pydantic v2** and **pydantic-settings** are the preferred tools.
- SQLAlchemy columns are declared as `Mapped[...]` annotations, with column options carried by `Annotated` types such as `Annotated[int, mapped_column(primary_key=True)]`. Never assign `= mapped_column(...)`: it returns `Any`, which hides a mismatch between a column and its annotation, and ty rejects it. An attribute SQLAlchemy supports only by assignment, such as `= relationship(...)`, carries `# ty: ignore[unsound-assignment]` on that line and nowhere else.

## API errors and forms

- Every API error reaches the Frontend as a thrown, typed error carrying the HTTP status and the response body.
- Every form shows the Backend's validation errors against the fields they belong to.

## Taskfile

- Every change that introduces a local action delivers its Taskfile task in the same change.
- CI and prek call tasks, never the underlying commands.

## Telemetry off

Nothing used may report usage or errors about the repository's owner. Version lookups and downloads are acceptable.
