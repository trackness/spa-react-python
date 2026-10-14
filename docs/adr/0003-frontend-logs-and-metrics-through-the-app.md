# Frontend logs and metrics go through the App, not OpenTelemetry

The Frontend posts its log records and measurements to the App's Receiving route. The App writes the logs to stdout and records the measurements alongside its own metrics. This makes both signals work in every Project with nothing configured, where OpenTelemetry in the browser would need a collector before either worked at all. Only Frontend traces use OpenTelemetry, sent to a URL held in a Setting.

## Consequences

- The App accepts only measurements it knows by name, so a new Frontend metric needs a matching Backend change.
- The Receiving route is public and always on, so it is size and rate limited, and Frontend log lines are marked as such.
