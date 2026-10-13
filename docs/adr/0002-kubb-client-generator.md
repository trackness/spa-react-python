# Kubb generates the TypeScript client

The TypeScript client is generated from FastAPI's OpenAPI document by Kubb, although FastAPI's own documentation names Hey API. In October 2026 Kubb, Orval and Hey API were each run against a real FastAPI application under TypeScript 7, and Kubb was the only one that both ran on a stable release and handled HTTP errors correctly without extra configuration.

## Considered Options

- **Hey API**: its stable release crashed under TypeScript 7; only an unreleased snapshot build worked.
- **Orval**: sent `null` query values as the text "null", dropped header parameters by default, and returned HTTP errors as ordinary data unless configured otherwise.
- **openapi-typescript**: declared unmaintained by its author in September 2026 and incompatible with TypeScript 7.

## Consequences

- The `exactOptionalPropertyTypes` compiler option stays off, because Kubb's output does not compile with it.
- Kubb's usage telemetry is on by default and must be disabled.
- Generated code is excluded from linting and formatting checks.
