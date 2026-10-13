# Frontend logs and metrics go through the app, not OpenTelemetry

The browser posts its log records and measurements to the app, which writes the logs to stdout and records the measurements alongside its own metrics. This makes both signals work in every Project with nothing configured, where OpenTelemetry in the browser would need a collector before either worked at all. Only frontend traces use OpenTelemetry, sent to a URL the Project configures.

## Consequences

- The app accepts only measurements it knows by name, so a new frontend metric needs a matching backend change.
- The receiving route is public and always on, so it is size and rate limited, and frontend log lines are marked as such.
